from bs4 import BeautifulSoup
from .utils import clean_content, content_by_density_analysis
import re


def extract_meta_data(html):
    """提取页面元数据"""
    soup = BeautifulSoup(html, 'html.parser')
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

def extract_title(html):
    """通用标题提取"""
    soup = BeautifulSoup(html, 'html.parser')
    meta_data = extract_meta_data(html)
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

def extract_content(html):
    """通用正文提取算法"""

    # 常见的内容容器类名和ID
    content_containers = [
        'article', 'content', 'post', 'main-content', 'article-content',
        'entry-content', 'post-content', 'article-body', 'main', 'story',
        'news-content', 'text', 'body', 'detail', 'container'
    ]

    soup = BeautifulSoup(html, 'html.parser')

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
    return content_by_density_analysis(soup)

def extract_publish_date(html):
    """提取发布日期"""
    soup = BeautifulSoup(html, 'html.parser')
    meta_data = extract_meta_data(html)

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