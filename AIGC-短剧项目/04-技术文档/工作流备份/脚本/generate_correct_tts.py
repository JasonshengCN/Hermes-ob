#!/usr/bin/env python3
"""
重新生成TTS音频，使用正确的30岁甜润音女声
"""

import requests
import json
import time
import os
from pathlib import Path
from datetime import datetime

class CorrectTTSGenerator:
    """正确的TTS音频生成器"""
    
    def __init__(self):
        self.api_key = "1f8f60420f204fa5b0e9ca5018791dbd"
        self.tts_workflow_id = "2044664193500057602"
        
        # 正确的音色描述
        self.correct_voice = "30岁甜润音女声：温柔亲和，语调软糯带着对生活的喜爱与温柔，像日常轻声说话一样松弛真实，带有轻微的气声和呼吸感，语气柔软舒展，充满对生活的细碎欢喜与温柔"
        
        # 项目目录
        self.project_dir = Path("/home/jason/aigc-douyin-project")
        self.output_dir = self.project_dir / "output" / "correct_tts_audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_tts(self, text, voice_description=None):
        """生成TTS音频"""
        if voice_description is None:
            voice_description = self.correct_voice
        
        print("🎤 生成正确的TTS音频")
        print("=" * 40)
        print(f"📝 文本长度: {len(text)} 字符")
        print(f"🎵 音色: {voice_description[:80]}...")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "apiKey": self.api_key,
            "workflowId": self.tts_workflow_id,
            "nodeInfoList": [
                {
                    "nodeId": "1",
                    "fieldName": "text",
                    "fieldValue": text
                },
                {
                    "nodeId": "2",
                    "fieldName": "text",
                    "fieldValue": voice_description
                }
            ],
            "retainSeconds": 600
        }
        
        try:
            response = requests.post(
                "https://www.runninghub.cn/task/openapi/create",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    task_id = result.get("data", {}).get("taskId")
                    print(f"✅ TTS任务创建成功! ID: {task_id}")
                    return task_id
                else:
                    print(f"❌ TTS任务创建失败: {result.get('msg')}")
                    return None
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None
    
    def check_task_status(self, task_id):
        """检查任务状态"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "apiKey": self.api_key,
            "taskId": task_id
        }
        
        try:
            response = requests.post(
                "https://www.runninghub.cn/task/openapi/status",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    data = result.get("data", {})
                    if isinstance(data, dict):
                        return data.get("taskStatus", "未知"), data.get("errorMsg", "")
                    else:
                        return str(data), ""
                else:
                    return "ERROR", result.get("msg", "未知错误")
            else:
                return f"HTTP_{response.status_code}", ""
                
        except Exception as e:
            return "EXCEPTION", str(e)
    
    def download_audio(self, task_id):
        """下载音频文件"""
        print(f"📥 下载音频文件: {task_id}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "apiKey": self.api_key,
            "taskId": task_id
        }
        
        # 使用outputs接口
        outputs_url = "https://www.runninghub.cn/task/openapi/outputs"
        
        try:
            response = requests.post(
                outputs_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    outputs = result.get("data", [])
                    if outputs and isinstance(outputs, list):
                        for output in outputs:
                            file_url = output.get("fileUrl")
                            if file_url and any(ext in file_url.lower() for ext in ['.flac', '.mp3', '.wav', '.ogg']):
                                print(f"🔗 找到音频文件: {file_url}")
                                
                                # 下载文件
                                file_response = requests.get(file_url, timeout=30)
                                if file_response.status_code == 200:
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    filename = f"correct_tts_{timestamp}.flac"
                                    filepath = self.output_dir / filename
                                    
                                    with open(filepath, 'wb') as f:
                                        f.write(file_response.content)
                                    
                                    print(f"✅ 音频已下载: {filepath}")
                                    print(f"📊 文件大小: {os.path.getsize(filepath)} 字节")
                                    
                                    # 保存元数据
                                    metadata = {
                                        "task_id": task_id,
                                        "text_length": len(text) if 'text' in locals() else 0,
                                        "voice_description": self.correct_voice,
                                        "audio_file": str(filepath),
                                        "file_size": os.path.getsize(filepath),
                                        "generated_at": datetime.now().isoformat()
                                    }
                                    
                                    metadata_file = self.output_dir / f"metadata_{timestamp}.json"
                                    with open(metadata_file, 'w', encoding='utf-8') as f:
                                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                                    
                                    print(f"📋 元数据已保存: {metadata_file}")
                                    
                                    return str(filepath)
                                else:
                                    print(f"❌ 文件下载失败: {file_response.status_code}")
                    
                    print("❌ 没有找到音频文件")
                    return None
                else:
                    print(f"❌ 获取输出失败: {result.get('msg')}")
                    return None
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None
    
    def wait_for_completion(self, task_id, max_wait=600):
        """等待任务完成"""
        print(f"⏳ 等待TTS音频生成...")
        print(f"📋 任务ID: {task_id}")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            elapsed = int(time.time() - start_time)
            print(f"⏰ 已等待: {elapsed}秒", end="\r")
            
            status, error = self.check_task_status(task_id)
            if status == "SUCCESS":
                print(f"\n✅ TTS音频生成完成!")
                return True, None
            elif status == "FAILED":
                print(f"\n❌ TTS音频生成失败: {error}")
                return False, error
            elif status in ["RUNNING", "PENDING"]:
                time.sleep(30)
            else:
                print(f"\n❓ 未知状态: {status}")
                time.sleep(30)
        
        print(f"\n⏰ 超时! TTS音频未在{max_wait}秒内完成")
        return False, "超时"
    
    def generate_correct_audio(self, text):
        """生成正确的音频文件"""
        print("🚀 开始生成正确的TTS音频")
        print("=" * 50)
        
        # 1. 生成TTS
        task_id = self.generate_tts(text)
        if not task_id:
            print("❌ TTS任务创建失败")
            return None
        
        # 2. 等待完成
        success, error = self.wait_for_completion(task_id)
        if not success:
            print(f"❌ TTS生成失败: {error}")
            return None
        
        # 3. 下载音频
        audio_path = self.download_audio(task_id)
        if not audio_path:
            print("❌ 音频下载失败")
            return None
        
        print(f"\n✅ 正确的TTS音频已生成!")
        print(f"📁 文件路径: {audio_path}")
        print(f"🎵 音色: 30岁甜润音女声")
        
        return audio_path

def main():
    """主函数"""
    generator = CorrectTTSGenerator()
    
    # 测试文本
    test_text = """大家好，我是AI新闻小助手！今天是2026-04-20，为你带来最新的AI科技动态！

第一条新闻：DeepSeek发布V3.2版本，推理能力大幅提升
DeepSeek最新版本在数学推理和代码生成方面表现优异

第二条新闻：Stable Diffusion 3.5发布，图像生成质量显著改善  
新版本在文本到图像生成方面有重大突破

以上就是今天的AI新闻速递！记得点赞关注，明天继续为你带来最新资讯！"""
    
    # 生成正确的音频
    audio_path = generator.generate_correct_audio(test_text)
    
    if audio_path:
        print(f"\n🎯 下一步:")
        print(f"  1. 使用这个音频文件测试视频工作流")
        print(f"  2. 检查视频中的语音是否使用正确的音色")
        print(f"  3. 如果仍然有问题，可能是视频工作流的问题")
    else:
        print("\n❌ TTS音频生成失败")

if __name__ == "__main__":
    main()