import re

def safe_decode_html_bytes(html_bytes):

    try:
        html_content = html_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # 如果失败，尝试常见编码
        common_encodings = ['gb2312', 'gbk', 'gb18030', 'iso-8859-1', 'windows-1252']
        for encoding in common_encodings:
            try:
                html_content = html_bytes.decode(encoding)
                return html_content
            except:
                continue

        # 最后的备选方案：忽略错误
        html_content = html_bytes.decode('utf-8', errors='ignore')

    return html_content


def clean_content(content):
    """清理正文内容"""
    if not content:
        return ""

    # 删除多余空白行和空格
    content = re.sub(r'\n\s*\n', '\n', content)
    content = re.sub(r'\s+', ' ', content)

    # 删除常见的注入内容
    noise_patterns = [
        r'点击查看更多',
        r'关注我们的公众号',
        r'扫描下方二维码',
        r'版权声明：.*?$',
        r'文章来源：.*?$',
        r'责任编辑：.*?$',
        r'更多精彩内容，关注.*?$',
        r'本文为.*?原创.*?$',
        r'更多相关资讯，请关注.*?$',
        r'本文转自.*?$'
    ]

    for pattern in noise_patterns:
        content = re.sub(pattern, '', content)

    # 删除可能的电话号码
    content = re.sub(r'\d{3,4}[-\s]?\d{7,8}', '', content)

    # 清理空格
    content = content.strip()

    # 将多个换行符替换为单个换行符
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content

def content_by_density_analysis(soup):
    """通过文本密度分析找出正文"""
    noise_classes = [
        'sidebar', 'comment', 'footer', 'header', 'navigation', 'nav',
        'ad', 'advertisement', 'related', 'recommendation', 'social', 'share',
        'copyright', 'disclaimer', 'bottom', 'author-info', 'toolbar'
    ]

    paragraphs = soup.find_all(['p', 'div'])
    candidates = []

    for p in paragraphs:
        if len(p.get_text().strip()) < 30:  # 忽略短段落
            continue

        # 计算标签密度
        text_length = len(p.get_text().strip())
        html_length = len(str(p))

        if html_length == 0:
            continue

        text_density = text_length / html_length

        # 检查是否在噪声区域内
        is_noise = False
        for parent in p.parents:
            if parent.name and (parent.get('class') or parent.get('id')):
                class_str = ' '.join(parent.get('class', []))
                id_str = parent.get('id', '')

                for noise in noise_classes:
                    if (noise in class_str.lower() or noise in id_str.lower()):
                        is_noise = True
                        break

            if is_noise:
                break

        if not is_noise:
            candidates.append((p, text_density, text_length))

    # 按文本密度和长度排序
    candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)

    if candidates:
        # 选择密度最高的一些段落
        content_parts = [c[0].get_text().strip() for c in candidates[:10]]
        return clean_content('\n'.join(content_parts))

    return ""