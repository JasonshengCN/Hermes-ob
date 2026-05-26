#!/usr/bin/env python3
"""
RunningHub 首尾帧生视频工具
- 工作流: 2049389424517058561 (首尾帧生视频)
- 节点280: Load Image — fieldName=image (首帧图片)
- 节点281: Load Image — fieldName=image (尾帧图片)
- 节点282: CLIP Text Encode (Prompt) — fieldName=text (提示词)
- 节点236: 帧数 — fieldName=value (整数帧数, 81帧=约5秒)
- 触发方式: 在对话中输入 "首尾帧" + 首帧图片 + 尾帧图片 + 时长 + 提示词
"""

import os, sys, json, time, requests
from pathlib import Path
from datetime import datetime

# ============================================================
# 配置
# ============================================================
API_KEY="1f8f60420f204fa5b0e9ca5018791dbd"
WORKFLOW_ID = "2049389424517058561"
BASE_URL = "https://www.runninghub.cn"
OUTPUT_DIR = Path("/home/jason/aigc-douyin-project/output/t2i")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 帧数 ≈ 时长(秒) * 16
SECONDS_TO_FRAMES = 16

start_time = time.time()

def log(msg, end=None):
    elapsed = int(time.time() - start_time)
    ts = datetime.now().strftime("%H:%M:%S")
    if end:
        print(f"[{ts}] {msg}", end=end, flush=True)
    else:
        print(f"[{ts}] {msg}")

def upload_image(image_path):
    """上传图片到RunningHub"""
    fname = os.path.basename(image_path)
    log(f"  📤 上传图片: {fname}")
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (fname, f, 'image/png')}
            r = requests.post(f"{BASE_URL}/task/openapi/upload",
                             files=files, data={'apiKey': API_KEY}, timeout=60)
            result = r.json()
        if result.get("code") != 0:
            log(f"  ❌ 上传失败: {result.get('msg','')[:200]}")
            return None
        asset = result["data"]["fileName"]
        log(f"  ✅ 上传成功: {asset}")
        return asset
    except Exception as e:
        log(f"  ❌ 上传异常: {e}")
        return None

def create_task(first_asset, last_asset, prompt, frames):
    """创建首尾帧生视频任务"""
    log(f"  🎬 首尾帧生视频: 帧数={frames}, 提示词={prompt[:80]}...")
    
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID,
        "nodeInfoList": [
            {"nodeId": "280", "fieldName": "image", "fieldValue": first_asset},
            {"nodeId": "281", "fieldName": "image", "fieldValue": last_asset},
            {"nodeId": "282", "fieldName": "text", "fieldValue": prompt},
            {"nodeId": "236", "fieldName": "value", "fieldValue": str(frames)}
        ],
        "retainSeconds": 600
    }
    
    try:
        r = requests.post(f"{BASE_URL}/task/openapi/create",
                         json=payload, timeout=30)
        result = r.json()
    except Exception as e:
        log(f"  ❌ 任务创建异常: {e}")
        return None
    
    if result.get("code") != 0:
        log(f"  ❌ 任务创建失败: {json.dumps(result, ensure_ascii=False)[:300]}")
        return None
    
    task_id = result["data"]["taskId"]
    log(f"  ✅ 任务创建成功! ID: {task_id}")
    return task_id

def monitor_task(task_id, max_wait=600):
    """监控任务直到完成"""
    start = time.time()
    check_interval = 15
    
    while time.time() - start < max_wait:
        elapsed = int(time.time() - start)
        log(f"  ⏰ 已等待 {elapsed}秒...", end="\r")
        
        try:
            r = requests.post(f"{BASE_URL}/task/openapi/status",
                            json={"apiKey": API_KEY, "taskId": task_id}, timeout=10)
            data = r.json()
            status = data.get("data", "UNKNOWN")
            if isinstance(status, dict):
                status = status.get("taskStatus", "UNKNOWN")
            
            if status == "SUCCESS":
                log(f"  ✅ 视频生成完成! 耗时{int(time.time()-start)}秒")
                return True
            elif status in ("FAILED", "ERROR"):
                log(f"  ❌ 任务失败: {json.dumps(data, ensure_ascii=False)[:200]}")
                return False
        except Exception as e:
            log(f"  ⚠️ 检查状态异常: {e}")
        
        time.sleep(check_interval)
    
    log("  ❌ 任务超时")
    return False

def download_output(task_id):
    """下载生成的视频"""
    log(f"  📥 下载输出文件...")
    
    try:
        r = requests.post(f"{BASE_URL}/task/openapi/outputs",
                         json={"apiKey": API_KEY, "taskId": task_id}, timeout=30)
        outputs = r.json().get("data", [])
    except Exception as e:
        log(f"  ❌ 获取输出异常: {e}")
        return None
    
    if not outputs:
        log("  ❌ 未找到输出文件")
        return None
    
    downloaded = []
    for out in outputs:
        url = out.get("fileUrl", "")
        if not url:
            continue
        ext = os.path.splitext(url.split('?')[0].split('/')[-1])[1] or '.mp4'
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = OUTPUT_DIR / f"firstlast_{ts}_{task_id[-8:]}{ext}"
        
        try:
            vr = requests.get(url, timeout=300)
            if vr.status_code == 200:
                with open(fname, 'wb') as f:
                    f.write(vr.content)
                size_kb = len(vr.content) / 1024
                log(f"  ✅ 视频已下载: {fname.name} ({size_kb:.0f}KB)")
                downloaded.append(str(fname))
        except Exception as e:
            log(f"  ⚠️ 下载失败: {e}")
    
    return downloaded

def main():
    global start_time
    start_time = time.time()
    
    if len(sys.argv) < 4:
        print("用法: python3 first_last_to_video.py <首帧图片路径> <尾帧图片路径> <时长秒数> [提示词]")
        print("示例: python3 first_last_to_video.py /path/to/first.png /path/to/last.png 5 '古风汉服缓缓苏醒'")
        print("说明: 时长将自动转换为帧数 (帧数 = 时长 × 16)")
        sys.exit(1)
    
    first_image = sys.argv[1]
    last_image = sys.argv[2]
    duration = int(sys.argv[3])
    frames = duration * SECONDS_TO_FRAMES + 1  # 81帧=5秒 => 帧数 = 时长*16+1
    prompt = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
    
    for img, label in [(first_image, "首帧"), (last_image, "尾帧")]:
        if not os.path.exists(img):
            print(f"❌ {label}图片不存在: {img}")
            sys.exit(1)
    
    print(f"\n{'='*55}")
    print(f"🎬 RunningHub 首尾帧生视频")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖼️ 首帧: {first_image}")
    print(f"🖼️ 尾帧: {last_image}")
    print(f"⏱️ 时长: {duration}秒 → 帧数: {frames}")
    print(f"💡 提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print(f"{'='*55}")
    
    # 1. 上传首帧
    log(f"📤 上传首帧图片...")
    first_asset = upload_image(first_image)
    if not first_asset:
        return False
    
    # 2. 上传尾帧
    log(f"📤 上传尾帧图片...")
    last_asset = upload_image(last_image)
    if not last_asset:
        return False
    
    # 3. 创建任务
    task_id = create_task(first_asset, last_asset, prompt, frames)
    if not task_id:
        return False
    
    # 4. 监控任务
    if not monitor_task(task_id, max_wait=600):
        return False
    
    # 5. 下载视频
    files = download_output(task_id)
    if not files:
        return False
    
    print(f"\n{'='*55}")
    print(f"🎉 首尾帧生视频完成!")
    total_min = (time.time() - start_time) / 60
    for f in files:
        print(f"  ✅ {f}")
    print(f"📊 总耗时: {total_min:.1f} 分钟")
    print(f"{'='*55}")
    
    for f in files:
        print(f"\nMEDIA:{f}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
