#!/usr/bin/env python3
"""
RunningHub 图生视频工具
- 工作流: 2049387851611119618 (图生视频)
- 节点286: Load Image — fieldName=image (输入图片)
- 节点287: CLIP Text Encode (Prompt) — fieldName=text (提示词)
- 节点271: 视频时长 — fieldName=value (整数秒)
- 触发方式: 在对话中输入 "图生视频" + 图片 + 时长 + 提示词
"""

import os, sys, json, time, requests
from pathlib import Path
from datetime import datetime

# ============================================================
# 配置
# ============================================================
API_KEY="1f8f60420f204fa5b0e9ca5018791dbd"
WORKFLOW_ID = "2049387851611119618"
BASE_URL = "https://www.runninghub.cn"
OUTPUT_DIR = Path("/home/jason/aigc-douyin-project/output/t2i")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

def create_task(image_asset, prompt, duration, width=576, height=1024):
    """创建图生视频任务"""
    log(f"  🎬 图生视频: {width}×{height}, 时长={duration}秒, 提示词={prompt[:80]}...")
    
    node_list = [
        {"nodeId": "286", "fieldName": "image", "fieldValue": image_asset},
        {"nodeId": "287", "fieldName": "text", "fieldValue": prompt},
        {"nodeId": "271", "fieldName": "Value", "fieldValue": str(duration)},
        {"nodeId": "275", "fieldName": "value", "fieldValue": str(height)},
        {"nodeId": "276", "fieldName": "value", "fieldValue": str(width)}
    ]
    
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID,
        "nodeInfoList": node_list,
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
        fname = OUTPUT_DIR / f"img2vid_{ts}_{task_id[-8:]}{ext}"
        
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
    
    if len(sys.argv) < 3:
        print("用法: python3 image_to_video.py <图片路径> <时长秒数> [提示词]")
        print("可选环境变量: WIDTH=1080 HEIGHT=1920 (默认竖屏 576×1024)")
        print("示例: python3 image_to_video.py /path/to/image.png 5 '古风汉服美女缓缓苏醒'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    duration = int(sys.argv[2])
    prompt = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
    
    # 分辨率参数：环境变量或默认竖屏
    width = int(os.environ.get("WIDTH", "576"))
    height = int(os.environ.get("HEIGHT", "1024"))
    
    if not os.path.exists(image_path):
        sys.exit(1)
    
    print(f"\n{'='*55}")
    print(f"🎬 RunningHub 图生视频")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖼️ 图片: {image_path}")
    print(f"⏱️ 时长: {duration}秒")
    print(f"📐 分辨率: {width}×{height}")
    print(f"💡 提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print(f"{'='*55}")
    
    # 1. 上传图片
    image_asset = upload_image(image_path)
    if not image_asset:
        return False
    
    # 2. 创建任务
    task_id = create_task(image_asset, prompt, duration, width, height)
    if not task_id:
        return False
    
    # 3. 监控任务
    if not monitor_task(task_id, max_wait=600):
        return False
    
    # 4. 下载视频
    files = download_output(task_id)
    if not files:
        return False
    
    print(f"\n{'='*55}")
    print(f"🎉 图生视频完成!")
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
