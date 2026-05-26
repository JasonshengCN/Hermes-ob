# 抖音AIGC新闻视频项目 - API密钥配置
# 重要：此文件包含敏感信息，请勿分享或提交到版本控制系统

import os
from pathlib import Path

class Config:
    """项目配置类"""
    
    # 项目路径
    PROJECT_ROOT = Path("/home/jason/aigc-douyin-project")
    DATA_DIR = PROJECT_ROOT / "data"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # API密钥配置
    TAVILY_API_KEY = "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"
    DEEPSEEK_API_KEY = "sk-8ec1b407f1154613ac833ca900b0c33b"
    RUNNINGHUB_API_KEY = "1f8f60420f204fa5b0e9ca5018791dbd"
    
    # RunningHub工作流ID
    TTS_WORKFLOW_ID = "2044664193500057602"  # 已验证的TTS工作流
    VIDEO_WORKFLOW_ID = None  # 待提供：WanInfiniteTalkToVideo工作流ID
    
    # 抖音配置
    DOUYIN_CONFIG = {
        "video_duration": 45,  # 视频时长(秒)
        "news_count": 3,  # 每次推送的新闻条数
        "push_time": "07:30",  # 每日推送时间
        "character_style": "高挑漂亮中国邻家妹子",  # 数字人形象
        "format": "vertical",  # 竖屏格式
        "tts_voice": "zh-CN-XiaoxiaoNeural",  # TTS语音(如果支持)
    }
    
    # Tavily新闻搜索配置
    TAVILY_CONFIG = {
        "search_depth": "advanced",  # 搜索深度
        "max_results": 10,  # 最大结果数
        "include_answer": True,  # 是否包含答案
        "include_raw_content": True,  # 是否包含原始内容
        "time_range": "day",  # 时间范围：day/week/month/year
    }
    
    # DeepSeek API配置
    DEEPSEEK_CONFIG = {
        "model": "deepseek-chat",  # 使用deepseek-chat模型
        "temperature": 0.7,  # 创意度
        "max_tokens": 1000,  # 最大输出token数
        "top_p": 0.9,  # 核采样
    }
    
    # RunningHub API配置
    RUNNINGHUB_CONFIG = {
        "base_url": "https://www.runninghub.cn",
        "timeout": 30,  # 请求超时时间(秒)
        "retain_seconds": 60,  # 任务保留时间(秒)
    }
    
    @classmethod
    def setup_directories(cls):
        """创建项目目录结构"""
        directories = [cls.DATA_DIR, cls.OUTPUT_DIR, cls.LOGS_DIR]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建目录: {directory}")
    
    @classmethod
    def validate_keys(cls):
        """验证API密钥格式"""
        validations = []
        
        # Tavily API密钥验证
        if cls.TAVILY_API_KEY.startswith("tvly-dev-"):
            validations.append(("Tavily API密钥", "✅ 格式正确"))
        else:
            validations.append(("Tavily API密钥", "⚠️  格式可能不正确"))
        
        # DeepSeek API密钥验证
        if cls.DEEPSEEK_API_KEY.startswith("sk-"):
            validations.append(("DeepSeek API密钥", "✅ 格式正确"))
        else:
            validations.append(("DeepSeek API密钥", "⚠️  格式可能不正确"))
        
        # RunningHub API密钥验证
        if len(cls.RUNNINGHUB_API_KEY) == 32:
            validations.append(("RunningHub API密钥", "✅ 格式正确"))
        else:
            validations.append(("RunningHub API密钥", "⚠️  格式可能不正确"))
        
        return validations
    
    @classmethod
    def get_env_vars(cls):
        """获取环境变量格式的配置"""
        return {
            "TAVILY_API_KEY": cls.TAVILY_API_KEY,
            "DEEPSEEK_API_KEY": cls.DEEPSEEK_API_KEY,
            "RUNNINGHUB_API_KEY": cls.RUNNINGHUB_API_KEY,
        }

# 创建目录结构
Config.setup_directories()

# 验证密钥
print("🔐 API密钥验证结果:")
print("="*40)
for service, status in Config.validate_keys():
    print(f"{service:20} {status}")

print(f"\n📁 项目目录已创建:")
print(f"   数据目录: {Config.DATA_DIR}")
print(f"   输出目录: {Config.OUTPUT_DIR}")
print(f"   日志目录: {Config.LOGS_DIR}")

print(f"\n🎯 下一步:")
print(f"   1. 测试Tavily新闻收集")
print(f"   2. 测试DeepSeek脚本生成")
print(f"   3. 等待视频工作流ID")
print(f"   4. 集成完整管道")