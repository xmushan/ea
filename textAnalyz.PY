def analyze_sentiment_from_txt(filename='gold_analysis_2025-04-20_20-02-14.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 关键词判断
        if "多" in content:
            return "📈 分析结果偏利多，倾向做多策略"
        elif "空" in content:
            return "📉 分析结果偏利空，需谨慎做多或考虑做空"
        elif "中性" in content
            return "⚖️ 分析结果中性，建议观望"
        else:
            return "❓ 无明确信号，分析内容不包含常见关键词"

    except FileNotFoundError:
        return "🚫 文件未找到，请检查文件路径或名称是否正确"
