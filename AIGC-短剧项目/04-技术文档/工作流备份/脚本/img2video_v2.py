#!/usr/bin/env python3
"""RunningHub图生视频 - 工作流2057818925982900225
节点584: Load Image (接收上传的图片)
节点624: CR Text (接收视频提示词)
节点620: PrimitiveInt (最长边)
节点593: PrimitiveInt (视频秒数)
"""
import os, sys, json, time, requests
from pathlib import Path
from datetime import datetime

API_KEY = os.environ.get("RUNNINGHUB_API_KEY", "")
if not API_KEY:
    API_KEY = "1f8f60420f204fa5b0e9ca5018791dbd"

WORKFLOW_ID = "2057818925982900225"
BASE_URL = "https://www.runninghub.cn"
OUTPUT_DIR = Path("/home/jason/aigc-douyin-project/output/video")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

start_time = time.time()

def log(msg):
    elapsed = int(time.time() - start_time)
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def upload_image(image_path):
    """上传图片 - multipart/form-data方式"""
    log(f"上传图片: {os.path.basename(image_path)}...")
    with open(image_path, 'rb') as f:
        r = requests.post(
            f'{BASE_URL}/task/openapi/upload',
            data={'apiKey': API_KEY},
            files={'file': (os.path.basename(image_path), f, 'image/png')},
            timeout=60
        )
    data = r.json()
    if data.get('code') == 0:
        fn = data['data']['fileName']
        log(f"上传成功: {fn}")
        return fn
    else:
        log(f"上传失败: {json.dumps(data, ensure_ascii=False)[:200]}")
        return None

def create_video_task(image_filename, prompt, max_side=1280, seconds=6):
    """创建图生视频任务"""
    log(f"图生视频: {prompt[:80]}...")
    print(f"最长边: {max_side} | 时长: {seconds}秒")

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'apiKey': API_KEY,
        'workflowId': WORKFLOW_ID,
        'nodeInfoList': [
            {'nodeId': '584', 'fieldName': 'image', 'fieldValue': image_filename},
            {'nodeId': '624', 'fieldName': 'text', 'fieldValue': prompt},
            {'nodeId': '620', 'fieldName': 'value', 'fieldValue': str(max_side)},
            {'nodeId': '593', 'fieldName': 'value', 'fieldValue': str(seconds)}
        ],
        'retainSeconds': 600
    }
    
    r = requests.post(f'{BASE_URL}/task/openapi/create',
                      headers=headers, json=payload, timeout=30)
    result = r.json()
    if result.get('code') != 0:
        log(f"任务创建失败: {json.dumps(result, ensure_ascii=False)[:300]}")
        return None
    task_id = result['data']['taskId']
    log(f"✅ 任务创建成功! ID: {task_id}")
    return task_id

def monitor_task(task_id, max_wait=600):
    """轮询任务状态"""
    start = time.time()
    while time.time() - start < max_wait:
        elapsed = int(time.time() - start)
        print(f"  已等待 {elapsed}秒...", end="\r", flush=True)
        r = requests.post(f'{BASE_URL}/task/openapi/status',
                          json={'apiKey': API_KEY, 'taskId': task_id}, timeout=10)
        data = r.json()
        status = data.get('data', 'UNKNOWN')
        if isinstance(status, dict):
            status = status.get('taskStatus', 'UNKNOWN')
        if status == 'SUCCESS':
            log(f"✅ 视频生成完成! 耗时{int(time.time()-start)}秒")
            return True
        elif status in ('FAILED', 'ERROR'):
            log(f"❌ 任务失败: {json.dumps(data, ensure_ascii=False)[:200]}")
            return False
        time.sleep(15)
    log("⚠️ 超时")
    return False

def download_output(task_id, output_name=None):
    """下载生成视频"""
    r = requests.post(f'{BASE_URL}/task/openapi/outputs',
                      json={'apiKey': API_KEY, 'taskId': task_id}, timeout=30)
    data = r.json()
    if data.get('code') != 0 or not data.get('data'):
        log(f"下载信息获取失败: {json.dumps(data, ensure_ascii=False)[:200]}")
        return None
    
    outputs = data['data']
    for out in outputs:
        url = out.get('fileUrl', '')
        if not url:
            continue
        if not output_name:
            output_name = f"img2video_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        log(f"下载: {output_name}")
        r = requests.get(url, timeout=300)
        output_path = OUTPUT_DIR / output_name
        with open(output_path, 'wb') as f:
            f.write(r.content)
        log(f"✅ 已保存: {output_path} ({len(r.content)/1024/1024:.1f}MB)")
        return str(output_path)
    log("没有找到输出文件")
    return None

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='RunningHub图生视频')
    parser.add_argument('image', help='图片路径')
    parser.add_argument('prompt', nargs='?', default='', help='视频提示词')
    parser.add_argument('--seconds', type=int, default=6, help='视频时长(秒)')
    parser.add_argument('--max-side', type=int, default=1280, help='最长边像素')
    parser.add_argument('--output', help='输出文件名')
    args = parser.parse_args()

    if not args.prompt:
        args.prompt = input("请输入视频提示词: ").strip()

    image_path = args.image
    if not os.path.exists(image_path):
        print(f"图片不存在: {image_path}")
        sys.exit(1)

    image_asset = upload_image(image_path)
    if not image_asset:
        sys.exit(1)

    task_id = create_video_task(image_asset, args.prompt, args.max_side, args.seconds)
    if not task_id:
        sys.exit(1)

    if not monitor_task(task_id):
        sys.exit(1)

    output_path = download_output(task_id, args.output)
    if output_path:
        print(f"\n🎬 输出文件: {output_path}")
