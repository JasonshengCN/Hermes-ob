#!/usr/bin/env python3
"""RunningHub文生图工具 - V2带尺寸节点支持
- 工作流: 2049358468934541313 (文生图)
- 节点137: CLIP Text Encode (Prompt) — fieldName=text
- 节点216: CR SDXL Aspect Ratio — 可选尺寸节点
"""
import os, sys, json, time, requests, argparse
from pathlib import Path
from datetime import datetime

API_KEY = os.environ.get("RUNNINGHUB_API_KEY", "")
if not API_KEY:
    API_KEY = "1f8f60420f204fa5b0e9ca5018791dbd"

WORKFLOW_ID = "2049358468934541313"
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

def create_t2i_task(prompt, width=None, height=None):
    log(f"  🎨 文生图: {prompt[:80]}...")
    
    node_info_list = [
        {"nodeId": "137", "fieldName": "text", "fieldValue": prompt}
    ]
    
    # 如果指定了尺寸，添加CR SDXL Aspect Ratio节点(216)参数
    if width and height:
        log(f"  📐 尺寸: {width}×{height}")
        node_info_list.append({
            "nodeId": "216", "fieldName": "width", "fieldValue": str(width)
        })
        node_info_list.append({
            "nodeId": "216", "fieldName": "height", "fieldValue": str(height)
        })
    
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID,
        "nodeInfoList": node_info_list,
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

def monitor_task(task_id, max_wait=300):
    start = time.time()
    check_interval = 10
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
                log(f"  ✅ 文生图完成! 耗时{int(time.time()-start)}秒")
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
        ext = os.path.splitext(url.split('?')[0].split('/')[-1])[1] or '.png'
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = OUTPUT_DIR / f"t2i_{ts}_{task_id[-8:]}{ext}"
        try:
            vr = requests.get(url, timeout=120)
            if vr.status_code == 200:
                fname.write_bytes(vr.content)
                log(f"  ✅ 图片已下载: {fname.name} ({len(vr.content)//1024}KB)")
                downloaded.append(str(fname))
            else:
                log(f"  ❌ 下载失败: HTTP {vr.status_code}")
        except Exception as e:
            log(f"  ❌ 下载异常: {e}")
    return downloaded

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RunningHub文生图")
    parser.add_argument("--prompt", "-p", required=True, help="文生图提示词")
    parser.add_argument("--output", "-o", help="输出文件名")
    parser.add_argument("--width", "-w", type=int, default=None, help="图片宽度")
    parser.add_argument("--height", "-H", type=int, default=None, help="图片高度")
    args = parser.parse_args()
    
    print("=" * 55)
    log(f"🔄 RunningHub 文生图（带尺寸支持）")
    log(f"🌐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)
    
    prompt = args.prompt
    task_id = create_t2i_task(prompt, args.width, args.height)
    if not task_id:
        sys.exit(1)
    
    if not monitor_task(task_id):
        sys.exit(1)
    
    files = download_output(task_id)
    if not files:
        sys.exit(1)
    
    print("=" * 55)
    log(f"🎉 文生图完成!")
    for f in files:
        log(f"  ✅ {f}")
    total = int(time.time() - start_time)
    log(f"📊 总耗时: {total//60}.{total%60} 分钟")
    print("=" * 55)
