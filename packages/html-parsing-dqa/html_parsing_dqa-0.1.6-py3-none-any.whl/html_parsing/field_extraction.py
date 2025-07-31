from bs4 import BeautifulSoup
from tika import language
from .utils import clean_content, content_by_density_analysis
import re
from datetime import datetime, timedelta
from dateutil.parser import parse

# todo: 1. 将入参改为soup； 2. 升级publish date的抽取函数； 3. 正文抽取加兜底

def extract_language(soup):
    """
        从HTML属性中检测语言
        """
    res = language.from_buffer(soup.get_text())

    return res

def extract_meta_data(soup):
    """提取页面元数据"""
    meta_data = {}

    # 提取所有meta标签信息
    meta_tags = soup.find_all('meta')
    for tag in meta_tags:
        property_value = tag.get('property', tag.get('name', ''))
        if property_value and tag.get('content'):
            meta_data[property_value] = tag.get('content')

    # 提取JSON-LD结构化数据
    json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
    if json_ld_scripts:
        import json
        for script in json_ld_scripts:
            try:
                if script.string:
                    ld_data = json.loads(script.string)
                    meta_data['json_ld'] = ld_data
                    break  # 只使用第一个有效的JSON-LD数据
            except Exception:
                continue

    return meta_data

def extract_title(soup):
    """通用标题提取"""
    meta_data = extract_meta_data(soup)
    # 按优先级提取标题
    title_candidates = [
        meta_data.get('og:title'),
        meta_data.get('twitter:title'),
        meta_data.get('title'),
        soup.find('title').get_text() if soup.find('title') else None,
    ]

    # 查找页面中的H1标签
    h1_tags = soup.find_all('h1')
    if h1_tags:
        title_candidates.append(h1_tags[0].get_text().strip())

    # 返回第一个非空标题
    for title in title_candidates:
        if title and title.strip():
            return title.strip()

    return ""

def extract_content(soup):
    """通用正文提取算法"""

    # 常见的内容容器类名和ID
    content_containers = [
        'article', 'content', 'post', 'main-content', 'article-content',
        'entry-content', 'post-content', 'article-body', 'main', 'story',
        'news-content', 'text', 'body', 'detail', 'container'
    ]

    # 1. 尝试找出语义化标签
    article_tag = soup.find('article')
    if article_tag:
        return clean_content(article_tag.get_text())

    # 2. 查找可能的内容容器
    for container in content_containers:
        container_tag = soup.find(['div', 'section', 'main'], class_=lambda x: x and container in x.lower())
        if not container_tag:
            container_tag = soup.find(['div', 'section', 'main'], id=lambda x: x and container in x.lower())

        if container_tag:
            return clean_content(container_tag.get_text())

    # 3. 密度分析
    content_density = content_by_density_analysis(soup)
    return content_density if len(content_density) > 20 else soup.get_text()

def extract_publish_date(html):
    """提取发布日期"""
    soup = BeautifulSoup(html, 'html.parser')
    meta_data = extract_meta_data(soup)

    # 1. 从元数据中查找
    date_meta_keys = ['article:published_time', 'og:published_time', 'publication_date',
                      'publishdate', 'publish_date', 'date']

    for key in date_meta_keys:
        if key in meta_data:
            return meta_data[key]

    # 2. 从JSON-LD结构化数据中提取
    if 'json_ld' in meta_data:
        json_ld = meta_data['json_ld']
        if isinstance(json_ld, dict):
            if 'datePublished' in json_ld:
                return json_ld['datePublished']
            elif '@graph' in json_ld:
                for item in json_ld['@graph']:
                    if isinstance(item, dict) and 'datePublished' in item:
                        return item['datePublished']

    # 3. 从HTML中查找时间标签
    date_containers = [
        ('time', {}),
        ('span', {'class': lambda c: c and any(x in c.lower() for x in ['time', 'date', 'publish'])}),
        ('div', {'class': lambda c: c and any(x in c.lower() for x in ['time', 'date', 'publish'])})
    ]

    for tag_name, attrs in date_containers:
        tags = soup.find_all(tag_name, attrs)
        for tag in tags:
            if tag.get('datetime'):
                return tag.get('datetime')
            elif tag.get_text().strip():
                # 使用正则表达式匹配日期格式
                date_text = tag.get_text().strip()
                # 常见日期格式：2023-01-01, 2023年01月01日, 2023/01/01, 01 Jan 2023等
                date_patterns = [
                    r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)',
                    r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
                    r'(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4})'
                ]

                for pattern in date_patterns:
                    date_match = re.search(pattern, date_text)
                    if date_match:
                        return date_match.group(1)

    # 4. 使用正则表达式直接从HTML内容中提取
    date_patterns_in_html = [
        r'发布时间[：:]\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)',
        r'发表于[：:]\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)',
        r'publish(?:ed)?\s*[date|time][：:]*\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)'
    ]

    for pattern in date_patterns_in_html:
        date_match = re.search(pattern, html)
        if date_match:
            return date_match.group(1)

    return ""


def extract_publish_date_iso(soup):

    def is_valid_dt(dt):
        """
        验证日期时间的合法性：
        1. 验证时区偏移是否在合法范围内（不超过24小时）
        2. 确保输入日期不超过当前日期
        """
        # 检查是否超过当前日期
        current_dt = datetime.now(dt.tzinfo if dt.tzinfo else None)
        if dt > current_dt:
            return False

        # 验证时区偏移合法性
        if dt.tzinfo:
            offset = dt.utcoffset()
            return abs(offset) <= timedelta(hours=24)

        return True

    def process_dates(dates_list):
        """处理日期列表返回结果"""
        if not dates_list:
            return None
        if len(dates_list) == 1:
            return dates_list[0].isoformat()

        base_date = dates_list[0].date()
        if all(dt.date() == base_date for dt in dates_list):
            earliest_dt = min(dates_list, key=lambda x: x.replace(tzinfo=None))
            return earliest_dt.isoformat()
        return None

    def extract_head_and_tail(text_content):
        length = len(text_content)
        # 只取头尾部的文本
        if length < 1000:
            text_content = text_content
        elif length < 2000:
            text_content = text_content[:int(0.4 * length)] + text_content[-int(0.2 * length):]
        elif length < 6000:
            text_content = text_content[:int(0.2 * length)] + text_content[-int(0.1 * length):]
        else:
            text_content = text_content[:int(0.1 * length)] + text_content[-int(0.1 * length):]

        return text_content

    explicit_candidates = []  # 明确标明的发布日期
    normal_candidates = []  # 普通日期

    # 1. 优先处理元数据（视为明确标明）
    known_names = [
        'date', 'pubdate', 'dc.date.issued', 'dc.date',
        'article.published', 'article:published_time',
        'og:article:published_time', 'datePublished'
    ]
    for meta in soup.find_all('meta'):
        attrs = [meta.get(attr) for attr in ('property', 'name', 'itemprop')]
        for attr in attrs:
            if attr and any(name in attr.lower() for name in known_names):
                explicit_candidates.append(meta.get('content'))

    # 2. 处理<time>元素（视为明确标明）
    for time_elem in soup.find_all('time'):
        dt_attr = time_elem.get('datetime')
        text = time_elem.get_text(strip=True)
        explicit_candidates.extend([dt_attr, text] if dt_attr else [text])

    # 3. 处理明确标明的正则表达式模式
    text_content = soup.get_text()
    text_content = text_content.replace('\n', '').replace('\t', '')
    text_content = re.sub(r'\s+', ' ', text_content)

    # 严格规则匹配，可以匹配全文
    explicit_patterns = [
        r'(?:发布时间|发表时间|发布日期|publish|发表于|更新时间|最后更新)[:：]\s*((?:\d{4}[-/.年]\d{1,2}[-/.月]\d{1,2})(?:\s+\d{1,2}:[0-5]\d(?::[0-5]\d)?)?)',
        r'(?:发布时间|发表时间|发布日期|publish|发表于|更新时间|最后更新)[:：]\s*((?:\d{4}-W\d{2}-\d)|(?:\d{4}-\d{3}))',  # ISO格式
        r'(?:发布时间|发表时间|发布日期|publish|发表于|更新时间|最后更新)[:：]\s*((?:\d{1,2}[/-]\d{1,2}[/-]\d{4})(?:\s+\d{1,2}:[0-5]\d)?)'
    ]

    for pattern in explicit_patterns:
        matches = re.findall(pattern, text_content)
        for match in matches:
            if isinstance(match, tuple):
                match = next((m for m in match if m), None)
            if match:
                explicit_candidates.append(match)


    text_content = extract_head_and_tail(text_content)


    if len(explicit_candidates) == 0:
        # 更宽松的规则匹配，只匹配头尾文本
        explicit_patterns_ = [
            r'(?:^|(?<=\s))(?:时间|日期)[:：]\s*((?:\d{4}[-/.年]\d{1,2}[-/.月]\d{1,2})(?:\s+\d{1,2}:[0-5]\d(?::[0-5]\d)?)?)',
            # r'(?:^|\s)(?:时间|日期)[:：]\s*((?:\d{4}[-/.年]\d{1,2}[-/.月]\d{1,2})(?:\s+\d{1,2}:[0-5]\d(?::[0-5]\d)?)?)',
            r'(?:^|(?<=\s))(?:时间|日期)[:：]\s*((?:\d{4}-W\d{2}-\d)|(?:\d{4}-\d{3}))',
            r'(?:^|(?<=\s))(?:时间|日期)[:：]\s*((?:\d{1,2}[/-]\d{1,2}[/-]\d{4})(?:\s+\d{1,2}:[0-5]\d)?)',
        ]

        for pattern in explicit_patterns_:
            matches = re.findall(pattern, text_content)
            for match in matches:
                if isinstance(match, tuple):
                    match = next((m for m in match if m), None)
                if match:
                    explicit_candidates.append(match)



    # 4. 处理普通日期正则表达式模式
    normal_patterns = [
        # r'(\d{4}[-/.年]\d{1,2}[-/.月]\d{1,2}(?: \d{1,2}:[0-5]\d(?::[0-5]\d)?)?)',
        r'(\d{4}[-/.年]\d{1,2}[-/.月]\d{1,2}[-/.日]?(?: \d{1,2}:[0-5]\d(?::[0-5]\d)?)?)', # 年月日+时间
        # r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})',  # 仅日期
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4}(?: \d{1,2}:[0-5]\d)?)',  # 日月年格式
        r'(\d{4}年\d{1,2}月\d{1,2}日(?: 上午|下午)?\d{1,2}(?::[0-5]\d)?)',  # 中文日期
        r'(\d{4}-W\d{2}-\d)',  # ISO周格式
        r'(\d{4}-\d{3})',  # ISO日序数格式
        r'(\d{4}[./-]\d{1,2}[./-]\d{1,2} \d{1,2}:[0-5]\d:\d{2})'  # 完整时间格式
    ]

    for pattern in normal_patterns:
        matches = re.findall(pattern, text_content)
        for match in matches:
            if isinstance(match, tuple):
                match = next((m for m in match if m), None)
            if match:
                normal_candidates.append(match)

    # print()
    # print(url)
    # print(text_content)
    # print(explicit_candidates)
    # print(normal_candidates)
    # pdb.set_trace()

    # 5. 处理明确标明的日期候选
    valid_explicit = []
    for candidate in explicit_candidates:
        if not candidate:
            continue
        try:
            candidate = candidate.replace('年', '-') # 年可能被误识别
            dt = parse(candidate, fuzzy=True)
            if is_valid_dt(dt):
                valid_explicit.append(dt)
        except (ValueError, TypeError):
            continue

    if valid_explicit:
        return process_dates(valid_explicit)

    # 6. 处理普通日期候选
    valid_normal = []
    for candidate in normal_candidates:
        if not candidate:
            continue
        try:
            candidate = candidate.replace('年', '-')  # 年可能被误识别
            dt = parse(candidate, fuzzy=True)
            if is_valid_dt(dt):
                valid_normal.append(dt)
        except (ValueError, TypeError):
            continue

    return process_dates(valid_normal) if valid_normal else None