#!/usr/bin/env python3
"""
智能动作提示词生成器
根据新闻内容和音频时长生成优化的动作提示词
"""

import re
from typing import List, Tuple

class ActionPromptOptimizer:
    """动作提示词优化器"""
    
    def __init__(self):
        # 动作词库
        self.action_words = {
            "开场": ["微笑", "亲切", "热情", "自信"],
            "播报": ["自然说话", "清晰表达", "流畅播报", "专业讲解"],
            "表情": ["表情专注", "神情认真", "面带微笑", "眼神交流"],
            "手势": ["手势自然", "适当手势", "肢体语言", "动作协调"],
            "过渡": ["轻微点头", "自然过渡", "语气转换", "节奏变化"],
            "强调": ["语气加重", "重点强调", "特别指出", "突出显示"],
            "总结": ["语气温和", "总结要点", "回顾重点", "归纳总结"],
            "结束": ["微笑结束", "感谢收看", "期待下次", "挥手告别"]
        }
        
        # 新闻类型对应的动作风格
        self.news_styles = {
            "技术发布": ["专业讲解", "技术细节", "分析影响", "行业趋势"],
            "产品更新": ["功能介绍", "使用演示", "优势对比", "用户体验"],
            "行业动态": ["市场分析", "竞争格局", "发展前景", "投资机会"],
            "研究突破": ["原理讲解", "实验过程", "成果意义", "未来应用"],
            "政策法规": ["政策解读", "影响分析", "合规建议", "实施时间"]
        }
    
    def analyze_news_content(self, news_text: str) -> dict:
        """分析新闻内容"""
        analysis = {
            "total_length": len(news_text),
            "paragraph_count": 0,
            "sentence_count": 0,
            "news_types": [],
            "key_topics": []
        }
        
        # 分割段落
        paragraphs = [p.strip() for p in news_text.split('\n\n') if p.strip()]
        analysis["paragraph_count"] = len(paragraphs)
        
        # 统计句子
        sentences = re.split(r'[。！？!?]', news_text)
        analysis["sentence_count"] = len([s for s in sentences if len(s.strip()) > 5])
        
        # 识别新闻类型
        news_text_lower = news_text.lower()
        type_keywords = {
            "技术发布": ["发布", "推出", "版本", "更新", "升级"],
            "产品更新": ["产品", "功能", "特性", "改进", "优化"],
            "行业动态": ["行业", "市场", "趋势", "发展", "竞争"],
            "研究突破": ["研究", "实验", "发现", "突破", "成果"],
            "政策法规": ["政策", "法规", "规定", "标准", "合规"]
        }
        
        for news_type, keywords in type_keywords.items():
            if any(keyword in news_text_lower for keyword in keywords):
                analysis["news_types"].append(news_type)
        
        # 提取关键词（简单实现）
        words = re.findall(r'[\u4e00-\u9fff]{2,4}', news_text)
        from collections import Counter
        word_freq = Counter(words)
        analysis["key_topics"] = [word for word, freq in word_freq.most_common(5) if freq > 1]
        
        return analysis
    
    def generate_action_lines(self, audio_duration: float, news_text: str) -> List[str]:
        """
        生成智能动作提示词
        
        参数:
        - audio_duration: 音频时长（秒）
        - news_text: 新闻文本
        
        返回:
        - 动作提示词列表（最多7行）
        """
        # 分析新闻内容
        analysis = self.analyze_news_content(news_text)
        
        print("📊 新闻分析结果:")
        print(f"  文本长度: {analysis['total_length']} 字符")
        print(f"  段落数量: {analysis['paragraph_count']} 段")
        print(f"  句子数量: {analysis['sentence_count']} 句")
        print(f"  新闻类型: {', '.join(analysis['news_types'])}")
        print(f"  关键话题: {', '.join(analysis['key_topics'][:3])}")
        
        # 计算分段策略
        max_lines = 7
        paragraph_count = analysis["paragraph_count"]
        
        # 根据段落数量决定分段策略
        if paragraph_count >= 5:
            # 多段落新闻：每段一个动作
            lines = self._generate_for_multi_paragraph(analysis, audio_duration)
        elif paragraph_count >= 3:
            # 中等段落：混合策略
            lines = self._generate_for_medium_paragraph(analysis, audio_duration)
        else:
            # 少段落：详细分解
            lines = self._generate_for_single_paragraph(analysis, audio_duration)
        
        # 确保不超过7行
        lines = lines[:max_lines]
        
        # 添加开场和结束
        if len(lines) < max_lines:
            lines = [self._get_opening_line()] + lines + [self._get_closing_line()]
        else:
            lines[0] = self._get_opening_line()
            lines[-1] = self._get_closing_line()
        
        return lines
    
    def _generate_for_multi_paragraph(self, analysis: dict, audio_duration: float) -> List[str]:
        """为多段落新闻生成动作提示词"""
        lines = []
        news_types = analysis["news_types"]
        key_topics = analysis["key_topics"]
        
        # 开场后的第一个动作
        if "技术发布" in news_types:
            lines.append("专业讲解，介绍技术原理")
        else:
            lines.append("自然说话，开始播报新闻")
        
        # 中间动作（根据段落数量）
        para_count = min(analysis["paragraph_count"], 4)  # 最多4个中间段
        
        for i in range(para_count):
            if i == 0 and key_topics:
                lines.append(f"表情专注，讲解{key_topics[0]}相关内容")
            elif i == 1:
                lines.append("手势自然，分析具体细节")
            elif i == 2:
                lines.append("语气加重，强调重点信息")
            else:
                lines.append("轻微点头，继续播报后续内容")
        
        # 总结动作
        lines.append("语气温和，总结今日要点")
        
        return lines
    
    def _generate_for_medium_paragraph(self, analysis: dict, audio_duration: float) -> List[str]:
        """为中等段落新闻生成动作提示词"""
        lines = []
        
        # 开场后的动作
        lines.append("自然说话，播报第一条新闻")
        lines.append("表情专注，详细讲解内容")
        
        # 根据新闻类型添加特定动作
        if "技术发布" in analysis["news_types"]:
            lines.append("手势自然，演示技术应用")
            lines.append("专业讲解，分析行业影响")
        elif "产品更新" in analysis["news_types"]:
            lines.append("适当手势，介绍产品功能")
            lines.append("清晰表达，对比优势特点")
        
        lines.append("语气温和，进行总结")
        
        return lines
    
    def _generate_for_single_paragraph(self, analysis: dict, audio_duration: float) -> List[str]:
        """为单段落新闻生成动作提示词"""
        lines = []
        
        # 将单条新闻分解为多个动作
        lines.append("自然说话，开始播报新闻")
        lines.append("表情专注，讲解主要内容")
        lines.append("手势自然，分析技术细节")
        lines.append("语气加重，强调关键信息")
        lines.append("轻微点头，补充相关背景")
        lines.append("语气温和，总结新闻要点")
        
        return lines
    
    def _get_opening_line(self) -> str:
        """获取开场动作"""
        import random
        openings = [
            "微笑，开始播报今日AI新闻",
            "亲切问候，带来最新科技动态",
            "自信开场，分享行业重要消息",
            "热情洋溢，介绍今日热点新闻"
        ]
        return random.choice(openings)
    
    def _get_closing_line(self) -> str:
        """获取结束动作"""
        import random
        closings = [
            "微笑结束，感谢收看",
            "挥手告别，期待下次再见",
            "亲切致谢，祝您有美好一天",
            "自然结束，我们下期再会"
        ]
        return random.choice(closings)
    
    def format_for_node254(self, action_lines: List[str]) -> str:
        """格式化为节点254需要的多行文本"""
        return "\n".join(action_lines)
    
    def validate_action_lines(self, action_lines: List[str], audio_duration: float) -> Tuple[bool, str]:
        """验证动作提示词"""
        if len(action_lines) > 7:
            return False, f"动作行数超过7行（当前{len(action_lines)}行）"
        
        if len(action_lines) < 2:
            return False, "动作行数太少，至少需要2行"
        
        # 检查每行长度
        for i, line in enumerate(action_lines, 1):
            if len(line) > 50:
                return False, f"第{i}行过长（{len(line)}字符），建议不超过50字符"
            if len(line.strip()) == 0:
                return False, f"第{i}行为空"
        
        # 计算预期的每段时长
        segment_count = len(action_lines)
        expected_segment_duration = audio_duration / segment_count
        
        if expected_segment_duration < 3:
            return False, f"分段过多，每段只有{expected_segment_duration:.1f}秒，建议减少分段"
        elif expected_segment_duration > 15:
            return False, f"分段过少，每段长达{expected_segment_duration:.1f}秒，建议增加分段"
        
        return True, f"验证通过：{segment_count}段，每段约{expected_segment_duration:.1f}秒"

# 使用示例
def example_usage():
    """使用示例"""
    optimizer = ActionPromptOptimizer()
    
    # 示例新闻
    example_news = """大家好，我是AI新闻小助手！今天是2026-04-20，为你带来最新的AI科技动态！

第一条新闻：DeepSeek发布V3.2版本，推理能力大幅提升。DeepSeek最新版本在数学推理和代码生成方面表现优异，比上一版本提升30%。

第二条新闻：谷歌推出多模态AI模型，支持图像、文本、音频联合处理。该模型在多个基准测试中取得领先成绩。

第三条新闻：国内AI芯片公司发布新一代处理器，算力提升5倍，能效比优化40%，将大幅降低AI计算成本。"""
    
    # 音频时长
    audio_duration = 63.2  # 秒
    
    print("🧠 智能动作提示词生成示例")
    print("=" * 60)
    
    # 生成动作提示词
    action_lines = optimizer.generate_action_lines(audio_duration, example_news)
    
    print("\n📝 生成的动作提示词:")
    for i, line in enumerate(action_lines, 1):
        print(f"  第{i}段: {line}")
    
    # 验证
    is_valid, message = optimizer.validate_action_lines(action_lines, audio_duration)
    print(f"\n✅ 验证结果: {message}")
    
    # 格式化为节点254需要的文本
    formatted_text = optimizer.format_for_node254(action_lines)
    print(f"\n📋 节点254格式:")
    print(formatted_text)
    
    print(f"\n📊 分段统计:")
    print(f"  音频时长: {audio_duration}秒")
    print(f"  分段数量: {len(action_lines)}段")
    print(f"  每段时长: {audio_duration/len(action_lines):.1f}秒")
    print(f"  总视频时长: ≈{audio_duration}秒")

if __name__ == "__main__":
    example_usage()