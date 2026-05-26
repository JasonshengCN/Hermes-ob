#!/bin/bash
# 抖音AIGC新闻视频每日生产执行脚本 v2.0
# 支持MEDIA输出捕获并推送到微信

echo "========================================"
echo "抖音AIGC新闻视频每日生产开始"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

cd /home/jason/aigc-douyin-project

# 激活虚拟环境（如果需要）
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "已激活虚拟环境"
fi

# 执行生产脚本，捕获MEDIA输出
echo "执行生产脚本..."
LOG_FILE="logs/daily_production_$(date '+%Y%m%d_%H%M%S').log"
mkdir -p logs

python3 daily_production.py 2>&1 | tee "$LOG_FILE"

# 检查是否有MEDIA输出
MEDIA_PATH=$(grep "^MEDIA:" "$LOG_FILE" | tail -1 | sed 's/^MEDIA://')

if [ -n "$MEDIA_PATH" ] && [ -f "$MEDIA_PATH" ]; then
    echo ""
    echo "========================================"
    echo "✅ 视频已生成: $MEDIA_PATH"
    echo "文件大小: $(du -h "$MEDIA_PATH" | cut -f1)"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "⚠️ 未检测到视频文件输出"
    echo "请检查日志: $LOG_FILE"
    echo "========================================"
fi

EXIT_CODE=$?
echo "退出代码: $EXIT_CODE"
echo "日志: $LOG_FILE"
exit $EXIT_CODE
