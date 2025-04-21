import requests
import os
import json
from datetime import datetime,timedelta
from bs4 import BeautifulSoup
from ai import ai

# ====== 自定义关键词列表（你可以根据交易品种动态指定） ======
KEYWORDS = [
    "黄金", "美元", "美联储", "战争", "CPI", "特朗普"
]

now = datetime.now()
cutoff_date = now - timedelta(days=3)  # 最近3天内的新闻
API_KEY = "7c9970e14ec3d77c1a32566c7f8cadab"

def extract_main_content(soup):
    candidates = [
        'div.article', 'div.content', 'div#article', 'div#artibody', 'div#main-content', 'article'
    ]
    for selector in candidates:
        container = soup.select_one(selector)
        if container:
            paragraphs = container.find_all('p')
            content = '\n'.join(
                p.get_text().strip() for p in paragraphs
                if p.get_text().strip() and len(p.get_text().strip()) > 10
            )
            if len(content) > 50:
                return content

    all_paragraphs = soup.find_all('p')
    filtered = []
    for p in all_paragraphs:
        text = p.get_text().strip()
        if not text:
            continue
        if any(word in text for word in ['推荐阅读', '扫码', '微信', '广告', '分享到']):
            continue
        filtered.append(text)

    return '\n'.join(filtered)

def query_news_by_keyword(keyword):
    print(f"\n🔍 正在抓取关键词：{keyword}")
    response = requests.get(
        'https://apis.tianapi.com/world/index',
        params={
            'key': API_KEY,
            'word': keyword
        }
    )

    result_list = []

    if response.status_code == 200:
        data = response.json()
        for item in data.get('result', {}).get('newslist', []):
            # 解析时间
            ctime_str = item.get('ctime')
            try:
                pub_time = datetime.strptime(ctime_str, "%Y-%m-%d %H:%M")
            except:
                continue  # 如果解析失败，跳过这条新闻

            if pub_time < cutoff_date:
                continue  # 如果时间早于3天前，跳过

            url = item.get('url')
            title = item.get('title', '')
            if url:
                try:
                    detail_res = requests.get(url, timeout=10)
                    try:
                        html_text = detail_res.text.encode('latin1').decode('utf-8', errors='ignore')
                    except:
                        html_text = detail_res.text
                    soup = BeautifulSoup(html_text, 'html.parser')
                    main_content = extract_main_content(soup)
                    item['detail_content'] = main_content if main_content else "未能提取正文"
                except Exception as e:
                    item['detail_content'] = f"抓取失败: {e}"
            else:
                item['detail_content'] = "无正文链接"
            
            print(f"📰 标题：{title}")
            print(f"📅 日期：{ctime_str}")
            print(f"📄 摘要：{item['detail_content'][:100]}...\n")

            result_list.append(item)
    else:
        print(f"❌ 请求失败，状态码：{response.status_code}")
    
    return result_list

def get_all_news_and_save():
    all_results = []
    for kw in KEYWORDS:
        news_list = query_news_by_keyword(kw)
        all_results.extend(news_list)

    # 保存
    now = datetime.now()
    filename = now.strftime("news_%Y-%m-%d_%H-%M-%S.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 全部新闻已保存：{filename}")
    ai(filename)
