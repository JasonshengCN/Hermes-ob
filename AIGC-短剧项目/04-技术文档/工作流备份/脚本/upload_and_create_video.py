#!/usr/bin/env python3
"""上传音频+数字人图片到RunningHub，创建数字人口播视频"""
import requests
import json
import base64
import time
import sys
import uuid
import os

API_KEY = '1f8f60420f204fa5b0e9ca5018791dbd'
BASE_URL = 'https://www.runninghub.cn'

LONG_VIDEO_WORKFLOW = '2046235426792411137'  # 长视频工作流

def upload_file(file_path):
    """上传文件到RunningHub"""
    with open(file_path, 'rb') as f:
        content = base64.b64encode(f.read()).decode('utf-8')
    
    payload = {
        'apiKey': API_KEY,
        'fileName': os.path.basename(file_path),
        'fileContent': content
    }
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    resp = requests.post(f'{BASE_URL}/task/openapi/upload', 
                         headers=headers, json=payload, timeout=60)
    data = resp.json()
    print(f"  上传返回: code={data.get('code')}, fileName={data.get('data', {}).get('fileName', 'N/A')}")
    if data.get('code') == 0:
        return data['data']['fileName']
    else:
        raise Exception(f"上传失败: {data.get('msg')}")

def create_video_task(image_file_name, audio_file_name, action_text="微笑，自然说话，轻微点头，手势自然"):
    """创建数字人视频任务"""
    payload = {
        'apiKey': API_KEY,
        'workflowId': LONG_VIDEO_WORKFLOW,
        'clientId': str(uuid.uuid4()),
        'nodeInfoList': [
            {
                'nodeId': '133',
                'fieldName': 'image',
                'fieldValue': image_file_name
            },
            {
                'nodeId': '125',
                'fieldName': 'audio',
                'fieldValue': audio_file_name
            },
            {
                'nodeId': '135',
                'fieldName': 'positive_prompt',
                'fieldValue': action_text
            }
        ],
        'retainSeconds': 600
    }
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    resp = requests.post(f'{BASE_URL}/task/openapi/create', 
                         headers=headers, json=payload, timeout=30)
    data = resp.json()
    print(f"  创建任务返回: {json.dumps(data, ensure_ascii=False)}")
    if data.get('code') == 0:
        return data['data']['taskId']
    else:
        raise Exception(f"创建任务失败: {data.get('msg')}")

def query_task_status(task_id):
    """查询任务状态"""
    payload = {
        'apiKey': API_KEY,
        'taskId': task_id
    }
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    resp = requests.post(f'{BASE_URL}/task/openapi/status', 
                         headers=headers, json=payload, timeout=30)
    return resp.json()

def get_task_output(task_id):
    """获取任务输出"""
    payload = {
        'apiKey': API_KEY,
        'taskId': task_id,
        'clientId': str(uuid.uuid4())
    }
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    resp = requests.post(f'{BASE_URL}/task/openapi/outputs', 
                         headers=headers, json=payload, timeout=30)
    return resp.json()

def download_output(url, save_path):
    """下载输出文件"""
    resp = requests.get(url, timeout=120)
    with open(save_path, 'wb') as f:
        f.write(resp.content)
    return save_path

if __name__ == '__main__':
    audio_path = '/home/jason/.hermes/audio_cache/tts_20260506_180601.mp3'
    image_path = '/home/jason/aigc-douyin-project/assets/images/digital_human_small.png'
    output_dir = '/home/jason/aigc-douyin-project/output/video/'
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== 步骤1: 上传数字人图片 ===")
    image_file_name = upload_file(image_path)
    print(f"  图片fileName: {image_file_name}")
    
    print("\n=== 步骤2: 上传音频文件 ===")
    audio_file_name = upload_file(audio_path)
    print(f"  音频fileName: {audio_file_name}")
    
    print("\n=== 步骤3: 创建数字人视频任务 ===")
    task_id = create_video_task(image_file_name, audio_file_name)
    print(f"  任务ID: {task_id}")
    
    print("\n=== 步骤4: 轮询任务状态 ===")
    max_wait = 600  # 最长等10分钟
    interval = 15
    waited = 0
    while waited < max_wait:
        result = query_task_status(task_id)
        code = result.get('code')
        data = result.get('data', {})
        
        if isinstance(data, str):
            status = data
        elif isinstance(data, dict):
            status = data.get('status', 'UNKNOWN')
        else:
            status = 'UNKNOWN'
        
        print(f"  等待 {waited}s... 状态: {status} (code={code})", flush=True)
        
        if status == 'SUCCESS' or (isinstance(data, str) and data == 'SUCCESS'):
            print("\n=== 任务完成！===")
            break
        elif status == 'FAILED' or (isinstance(data, str) and data == 'FAILED'):
            print(f"\n❌ 任务失败! {result.get('msg', '')}")
            sys.exit(1)
        elif waited >= max_wait:
            print("\n⏰ 超时!")
            sys.exit(1)
        
        time.sleep(interval)
        waited += interval
    
    print("\n=== 步骤5: 获取输出 ===")
    output = get_task_output(task_id)
    print(f"  输出: {json.dumps(output, ensure_ascii=False)[:500]}")
    
    if output.get('code') == 0:
        outputs = output.get('data', {}).get('outputs', [])
        for i, out in enumerate(outputs):
            file_url = out.get('fileUrl', '')
            if file_url:
                save_path = os.path.join(output_dir, f'digital_human_video_{i}.mp4')
                print(f"  下载第{i+1}个输出: {file_url}")
                download_output(file_url, save_path)
                print(f"  保存到: {save_path}")
                print(f"\nMEDIA:{save_path}")
    
    print("\n✅ 完成!")
