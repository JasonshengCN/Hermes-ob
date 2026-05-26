import os, sys, json, time, requests, argparse
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.hermes/.env"))

ZNZ_API_KEY = os.getenv("ZNZ_API_KEY")
if not ZNZ_API_KEY:
    ZNZ_API_KEY = "sk-rFU1pMq1HlL3uEsFBq7Qop53GIPaIJ5KRIy8yKGi9DZ2gxM0"

API_BASE = "https://ai.t8star.org"
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

def gpt_image2_optimize(image_path, prompt=None):
    """使用GPT Image 2优化图片"""
    log(f"  🔄 GPT Image 2优化中: {os.path.basename(image_path)}...")
    
    if prompt:
        log(f"  📝 优化提示: {prompt[:100]}...")
    
    # 先获取图片的base64
    import base64
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    ext = os.path.splitext(image_path)[1].lower().lstrip(".")
    if ext in ("jpg", "jpeg"):
        mime = "image/jpeg"
    else:
        mime = f"image/{ext}"
    
    # 构建优化prompt
    if prompt:
        system_msg = prompt
    else:
        system_msg = "提升这张图片的画质和细节，保持原有构图、色彩和风格不变，让画面更清晰细腻，色彩更丰富自然，光影层次更分明。增强细节清晰度和整体质感，但不要改变原有内容。"
    
    headers = {
        "Authorization": f"Bearer {ZNZ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-image-2",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}", "detail": "high"}},
                    {"type": "text", "text": system_msg}
                ]
            }
        ],
        "n": 1
    }
    
    try:
        r = requests.post(f"{API_BASE}/v1/chat/completions",
                          headers=headers, json=payload, timeout=300)
        result = r.json()
    except Exception as e:
        log(f"  ❌ GPT Image 2调用异常: {e}")
        return None
    
    if "error" in result:
        log(f"  ❌ GPT Image 2错误: {json.dumps(result['error'], ensure_ascii=False)[:200]}")
        return None
    
    # 从response中提取图片
    try:
        content = result["choices"][0]["message"]["content"]
        # GPT Image 2返回的是markdown图片格式或base64
        if isinstance(content, str):
            if "data:image" in content:
                # base64格式
                import re
                match = re.search(r'data:image/[^;]+;base64,([^"\']+)', content)
                if match:
                    img_data = base64.b64decode(match.group(1))
                else:
                    # 尝试直接检查整个content是否为base64
                    try:
                        img_data = base64.b64decode(content)
                    except:
                        log(f"  ❌ 无法解析图片数据")
                        log(f"  📄 content[:200]: {content[:200]}")
                        return None
            elif "http" in content and ("png" in content or "jpg" in content or "jpeg" in content):
                # URL格式
                import re
                urls = re.findall(r'https?://[^\s\)"\']+\.(?:png|jpg|jpeg)', content)
                if urls:
                    img_url = urls[0]
                    log(f"  📥 下载优化图片: {img_url[:80]}...")
                    vr = requests.get(img_url, timeout=120)
                    if vr.status_code == 200:
                        img_data = vr.content
                    else:
                        log(f"  ❌ 下载失败: HTTP {vr.status_code}")
                        return None
                else:
                    log(f"  ❌ 未找到图片URL")
                    log(f"  📄 content[:200]: {content[:200]}")
                    return None
            else:
                log(f"  ❌ 未知的响应格式")
                log(f"  📄 content[:200]: {content[:200]}")
                return None
        else:
            log(f"  ❌ response内容非字符串")
            return None
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = OUTPUT_DIR / f"optimized_{ts}.png"
        fname.write_bytes(img_data)
        log(f"  ✅ 优化图片已保存: {fname.name} ({len(img_data)//1024}KB)")
        return str(fname)
        
    except Exception as e:
        log(f"  ❌ 处理优化结果异常: {e}")
        import traceback
        log(traceback.format_exc())
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GPT Image 2图片优化")
    parser.add_argument("--image", "-i", required=True, help="待优化的图片路径")
    parser.add_argument("--prompt", "-p", help="优化提示词（可选）", default=None)
    args = parser.parse_args()
    
    print("=" * 55)
    log(f"🔄 GPT Image 2 图片优化")
    log(f"🌐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)
    
    if not os.path.exists(args.image):
        log(f"  ❌ 图片不存在: {args.image}")
        sys.exit(1)
    
    result = gpt_image2_optimize(args.image, args.prompt)
    if result:
        print("=" * 55)
        log(f"🎉 优化完成!")
        log(f"  ✅ {result}")
        total = int(time.time() - start_time)
        log(f"📊 总耗时: {total//60}.{total%60} 分钟")
        print("=" * 55)
        print(f"\nMEDIA:{result}")
    else:
        log(f"  ❌ 优化失败")
        sys.exit(1)
