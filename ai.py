import json
from openai import OpenAI
from datetime import datetime,timedelta
import time
# 初始化OpenAI client
client = OpenAI(
    api_key = "sk-VS8Df0CNKUr7KpEP7em8acrPoTlsF3ckIR7p0BoiBPNvWLq9",
    base_url = "https://api.moonshot.cn/v1",
)

# 读取保存的新闻 JSON 文件
def load_news(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_news_in_batches(news, batch_size=5):
    batch_summaries = []
    total = len(news)
    batch_count = (total + batch_size - 1) // batch_size
    last_call_time = 0

    for i in range(batch_count):
        print(f"\n📦 正在处理第 {i+1}/{batch_count} 批新闻...")
        batch = news[i * batch_size: (i + 1) * batch_size]
        individual_impacts = []

        for item in batch:
            title = item.get('title')
            content = item.get('detail_content')
            if not title or not content:
                continue

            now = time.time()
            elapsed = now - last_call_time
            if elapsed < 21:
                sleep_time = 21 - elapsed
                print(f"⏳ 等待 {sleep_time:.1f} 秒避免触发限流...")
                time.sleep(sleep_time)
            last_call_time = time.time()

            try:
                short_content = content[:600]
                completion = client.chat.completions.create(
                    model="moonshot-v1-8k",
                    messages=[
                        {"role": "system", "content": "你是一个金融新闻分析师，擅长分析国际局势对黄金市场的影响。"},
                        {"role": "user", "content": f"请阅读以下新闻，并判断其对黄金价格的潜在影响（利多、利空、中性），并简要说明理由：\n\n标题：{title}\n内容：{short_content}"}
                    ],
                    temperature=0.7,
                )
                result = completion.choices[0].message.content.strip()
                print(f"✅ 分析完成：{title}")
                individual_impacts.append(f"📰 {title}\n📈 分析结果：{result}\n")

            except Exception as e:
                print(f"❌ AI 分析失败：{title}，错误：{e}")

        if not individual_impacts:
            continue

        # 本批总结
        print("🧠 正在生成当前批次小结...")
        now = time.time()
        elapsed = now - last_call_time
        if elapsed < 21:
            sleep_time = 21 - elapsed
            time.sleep(sleep_time)

        try:
            batch_prompt = "\n\n".join(individual_impacts)
            batch_summary = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "你是一个黄金交易顾问，擅长基于多条新闻分析市场影响。"},
                    {"role": "user", "content": f"以下是对部分新闻的黄金影响分析，请综合这些内容给出这一批新闻对黄金价格的总体影响（利多、利空、中性），并说明理由：\n\n{batch_prompt}"}
                ],
                temperature=0.7,
            )
            summary_text = batch_summary.choices[0].message.content.strip()
            batch_summaries.append(summary_text)
            print(f"📦 批次 {i+1} 小结完成。")

        except Exception as e:
            print(f"⚠️ 当前批次总结失败：{e}")

    # 综合所有批次小结
    print("\n📈 正在综合所有批次结论生成最终总结...")
    if not batch_summaries:
        return "未能生成任何批次总结，无法得出综合结论。"

    now = time.time()
    elapsed = now - last_call_time
    if elapsed < 21:
        time.sleep(21 - elapsed)

    try:
        final_input = "\n\n".join(batch_summaries)
        final_summary = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是资深黄金交易分析师，请综合判断当前国际新闻对黄金价格的总体趋势。"},
                {"role": "user", "content": f"以下是多批新闻总结，请你判断整体是利多、利空还是中性，只需要告诉我一个字，“多”，“空”，“中性”：\n\n{final_input}"}
            ],
            temperature=0.7,
        )
        return "📊 最终综合结论：\n" + final_summary.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ 最终综合分析失败：{str(e)}"



# 保存分析结果到文件
def save_analysis_results(analysis_results):
    now = datetime.now()
    filename = now.strftime("analysis_results_%Y-%m-%d_%H-%M-%S.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 分析结果已保存：{filename}")

# 主程序
def ai(filename):
    # filename = "news_2025-04-19_09-29-30.json"  # 替换为你的实际文件名
    news_data = load_news(filename)

    if isinstance(news_data, dict):
        news_list = news_data.get('result', {}).get('newslist', [])
    elif isinstance(news_data, list):
        news_list = news_data
    else:
        print("❌ 无效的 JSON 数据结构")
        return

    print(f"📦 共获取新闻：{len(news_list)} 条\n")

    conclusion = analyze_news_in_batches(news_list)

    print("📊 综合分析结论：\n")
    print(conclusion)

    now = datetime.now()
    output_filename = f"gold_analysis.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(conclusion)
    print(f"\n✅ 结果已保存至：{output_filename}")