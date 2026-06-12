#!/usr/bin/env python3
"""
Markdown to HTML Converter for Interview Prep Documents
Converts all markdown files in the source directory to responsive HTML files
"""

import os
import re
from pathlib import Path

# 源目录和目标目录
SOURCE_DIR = Path('G:/ai_project/study/面试准备')
TARGET_DIR = Path('G:/ai_project/study/html')

# 文件列表（按顺序）
FILES = [
    '01_Java基础.md',
    '02_JVM.md',
    '03_Spring.md',
    '04_MySQL.md',
    '05_Redis.md',
    '06_Elasticsearch.md',
    '07_Netty.md',
    '08_SpringWebFlux.md',
    '09_分布式系统.md',
    '10_DDD.md',
    '11_消息队列.md',
    '12_Linux与CI_CD.md',
    '深入原理_01_Java基础底层.md',
    '深入原理_02_JVM底层.md',
    '深入原理_03_MySQL底层.md',
    '深入原理_04_Redis底层.md',
    '深入原理_05_Spring底层.md',
]

def parse_markdown(content):
    """Parse markdown content to HTML"""

    # 处理标题（添加锚点）
    def process_heading(match):
        level = len(match.group(1))
        title = match.group(2).strip()
        anchor = generate_anchor(title)
        return f'<h{level} id="{anchor}">{title}</h{level}>'

    content = re.sub(r'^#{1,6}\s+(.+)$', process_heading, content, flags=re.MULTILINE)

    # 处理代码块
    content = re.sub(r'^```\w*\n(.*?)```', r'<pre><code>\1</code></pre>', content, flags=re.MULTILINE | re.DOTALL)

    # 处理行内代码
    content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)

    # 处理粗体
    content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)

    # 处理斜体
    content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', content)

    # 处理分隔线
    content = re.sub(r'^---+$', r'<hr>', content, flags=re.MULTILINE)

    # 处理引用块
    content = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', content, flags=re.MULTILINE)

    # 处理表格
    def process_table(content):
        lines = content.split('\n')
        table_lines = []
        in_table = False

        for i, line in enumerate(lines):
            if line.strip().startswith('|') and line.strip().endswith('|'):
                if not in_table:
                    in_table = True
                    table_lines.append('<table>')

                cells = [c.strip() for c in line.strip().split('|')[1:-1]]

                # 检查是否是分隔行
                if all(c.replace('-', '').replace(':', '') == '' for c in cells):
                    continue

                # 第一行是表头
                if table_lines[-1] == '<table>':
                    row = '<tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr>'
                else:
                    row = '<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>'

                table_lines.append(row)
            else:
                if in_table:
                    table_lines.append('</table>')
                    in_table = False
                table_lines.append(line)

        if in_table:
            table_lines.append('</table>')

        return '\n'.join(table_lines)

    content = process_table(content)

    # 处理列表
    def process_list(content):
        lines = content.split('\n')
        result = []
        in_ul = False
        in_ol = False

        for line in lines:
            stripped = line.strip()

            if stripped.startswith('- ') or stripped.startswith('* '):
                if in_ol:
                    result.append('</ol>')
                    in_ol = False
                if not in_ul:
                    result.append('<ul>')
                    in_ul = True
                result.append(f'<li>{stripped[2:]}</li>')
            elif re.match(r'^\d+\.\s+', stripped):
                if in_ul:
                    result.append('</ul>')
                    in_ul = False
                if not in_ol:
                    result.append('<ol>')
                    in_ol = True
                item = re.sub(r'^\d+\.\s+', '', stripped)
                result.append(f'<li>{item}</li>')
            else:
                if in_ul:
                    result.append('</ul>')
                    in_ul = False
                if in_ol:
                    result.append('</ol>')
                    in_ol = False
                result.append(line)

        if in_ul:
            result.append('</ul>')
        if in_ol:
            result.append('</ol>')

        return '\n'.join(result)

    content = process_list(content)

    # 处理段落（空行分隔）
    paragraphs = []
    lines = content.split('\n')
    current_para = []

    for line in lines:
        if line.strip() == '':
            if current_para:
                para_text = '\n'.join(current_para)
                # 如果不是已处理的元素，包装成段落
                if not any(para_text.strip().startswith(tag) for tag in ['<h', '<ul', '<ol', '<pre', '<table', '<blockquote', '<hr']):
                    para_text = f'<p>{para_text}</p>'
                paragraphs.append(para_text)
                current_para = []
        else:
            current_para.append(line)

    if current_para:
        para_text = '\n'.join(current_para)
        if not any(para_text.strip().startswith(tag) for tag in ['<h', '<ul', '<ol', '<pre', '<table', '<blockquote', '<hr']):
            para_text = f'<p>{para_text}</p>'
        paragraphs.append(para_text)

    return '\n\n'.join(paragraphs)

def generate_anchor(title):
    """Generate anchor from title"""
    # 移除特殊字符，转为小写，用连字符连接
    anchor = re.sub(r'[^\w\s-]', '', title)
    anchor = re.sub(r'\s+', '-', anchor)
    anchor = anchor.lower()
    return anchor

def generate_toc(content):
    """Generate table of contents from content"""
    toc = []

    headings = re.findall(r'^#{2,3}\s+(.+)$', content, flags=re.MULTILINE)

    toc.append('<ul class="level-2">')

    for heading in headings:
        level = 2 if heading.startswith('##') else 3
        title = re.sub(r'^#+\s+', '', heading)
        anchor = generate_anchor(title)

        if level == 2:
            toc.append(f'<li><a href="#{anchor}">{title}</a></li>')
        else:
            toc.append(f'<li class="level-3"><a href="#{anchor}">{title}</a></li>')

    toc.append('</ul>')

    return '\n'.join(toc)

def convert_file(source_file, target_file, prev_file, next_file):
    """Convert a single markdown file to HTML"""

    # 读取模板
    template_path = TARGET_DIR / 'template.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # 读取源文件
    source_path = SOURCE_DIR / source_file
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取标题（第一行）
    title_match = re.match(r'^#\s+(.+)$', content)
    if title_match:
        title = title_match.group(1)
        content = content[content.find('\n')+1:]  # 移除标题行
    else:
        title = source_file.replace('.md', '')

    # 生成目录
    toc = generate_toc(content)

    # 解析内容
    html_content = parse_markdown(content)

    # 替换模板变量
    html = template.replace('{{TITLE}}', title)
    html = html.replace('{{TOC}}', toc)
    html = html.replace('{{CONTENT}}', html_content)
    html = html.replace('{{PREV_PAGE}}', prev_file if prev_file else 'index.html')
    html = html.replace('{{NEXT_PAGE}}', next_file if next_file else 'index.html')

    # 写入目标文件
    target_path = TARGET_DIR / target_file
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'Converted: {source_file} -> {target_file}')

def main():
    """Main conversion process"""

    # 确保目标目录存在
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    # 转换所有文件
    for i, source_file in enumerate(FILES):
        # 生成目标文件名
        target_file = source_file.replace('.md', '.html')

        # 确定前后文件
        prev_file = FILES[i-1].replace('.md', '.html') if i > 0 else None
        next_file = FILES[i+1].replace('.md', '.html') if i < len(FILES) - 1 else None

        convert_file(source_file, target_file, prev_file, next_file)

    print(f'\nConversion complete! {len(FILES)} files converted.')
    print(f'Output directory: {TARGET_DIR}')

if __name__ == '__main__':
    main()