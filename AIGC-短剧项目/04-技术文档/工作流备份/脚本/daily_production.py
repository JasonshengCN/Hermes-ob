#!/usr/bin/env python3
"""
抖音AIGC新闻视频每日生产 - 入口脚本
调用完整的生产管道
"""
import os
import sys
import subprocess
from datetime import datetime

project_dir = '/home/jason/aigc-douyin-project'
log_dir = os.path.join(project_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"daily_production_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

print(f"========================================")
print(f"抖音AIGC新闻视频每日生产")
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"脚本: production_pipeline.py")
print(f"日志: {log_file}")
print(f"========================================")

result = subprocess.run(
    ['python3', 'production_pipeline.py'],
    cwd=project_dir,
    capture_output=True,
    text=True,
    timeout=3600  # 60分钟超时
)

# 保存完整日志
with open(log_file, 'w', encoding='utf-8') as f:
    f.write(result.stdout)
    if result.stderr:
        f.write("\n\n=== STDERR ===\n")
        f.write(result.stderr)

# 输出到stdout
print(result.stdout)
if result.stderr:
    print(f"\n=== STDERR ===\n{result.stderr[:1000]}")

# 检查MEDIA输出
for line in result.stdout.split('\n'):
    line = line.strip()
    if line.startswith('MEDIA:'):
        media_path = line.split(':', 1)[1].strip()
        if os.path.exists(media_path):
            file_size = os.path.getsize(media_path)
            print(f"\n✅ 视频文件确认: {media_path} ({file_size/1024/1024:.2f}MB)")
        break

print(f"\n退出代码: {result.returncode}")
sys.exit(result.returncode)
