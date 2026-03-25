#!/usr/bin/env python3
"""
静态站点生成器
将Markdown文章转换为HTML静态页面
"""

import os
import re
import markdown
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class SiteGenerator:
    def __init__(self):
        self.content_dir = "content"
        self.template_dir = "templates"
        self.output_dir = "public"
        
        # Jinja2环境
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # Markdown转换器
        self.md = markdown.Markdown(extensions=['extra', 'codehilite'])
        
        # 站点配置
        self.site_config = {
            'title': 'AI副业指南',
            'description': '分享AI工具、副业技巧、赚钱方法',
            'year': datetime.now().year
        }
    
    def parse_markdown(self, filepath):
        """解析Markdown文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题（第一个#开头的行）
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else '无标题'
        
        # 提取日期（从文件名或内容）
        filename = os.path.basename(filepath)
        date_match = re.search(r'^(\d{4}-\d{2}-\d{2})', filename)
        date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
        
        # 提取摘要（前200字）
        text = re.sub(r'#+ ', '', content)  # 移除标题标记
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # 移除链接
        summary = text[:200] + '...' if len(text) > 200 else text
        
        # 转换为HTML
        html_content = self.md.convert(content)
        self.md.reset()
        
        return {
            'title': title,
            'date': date,
            'summary': summary,
            'content': html_content,
            'filename': filename.replace('.md', '.html')
        }
    
    def generate_article_page(self, article):
        """生成文章页面"""
        template = self.env.get_template('article.html')
        
        html = template.render(
            title=article['title'],
            date=article['date'],
            content=article['content'],
            site_title=self.site_config['title'],
            year=self.site_config['year']
        )
        
        output_path = os.path.join(self.output_dir, article['filename'])
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return article['filename']
    
    def generate_index_page(self, articles):
        """生成首页"""
        template = self.env.get_template('index.html')
        
        # 按日期排序
        articles_sorted = sorted(articles, key=lambda x: x['date'], reverse=True)
        
        # 准备文章列表数据
        article_list = []
        for article in articles_sorted:
            article_list.append({
                'title': article['title'],
                'date': article['date'],
                'summary': article['summary'],
                'url': article['filename']
            })
        
        html = template.render(
            articles=article_list,
            site_title=self.site_config['title'],
            site_description=self.site_config['description'],
            year=self.site_config['year']
        )
        
        output_path = os.path.join(self.output_dir, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def generate(self):
        """生成整个站点"""
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 读取所有文章
        articles = []
        for filename in os.listdir(self.content_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.content_dir, filename)
                article = self.parse_markdown(filepath)
                articles.append(article)
                
                # 生成文章页面
                self.generate_article_page(article)
                print(f"✅ 生成文章: {article['title']}")
        
        # 生成首页
        self.generate_index_page(articles)
        print(f"✅ 生成首页")
        
        print(f"\n🎉 站点生成完成！共 {len(articles)} 篇文章")
        print(f"输出目录: {os.path.abspath(self.output_dir)}")


def main():
    """主函数"""
    generator = SiteGenerator()
    generator.generate()


if __name__ == "__main__":
    main()
