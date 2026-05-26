#!/bin/bash
# 抖音AIGC新闻视频每日生产定时任务脚本

echo "设置抖音AIGC新闻视频每日生产定时任务..."
echo "任务时间：每天早上7:30"
echo "项目目录：/home/jason/aigc-douyin-project"

# 创建日志目录
LOG_DIR="/home/jason/aigc-douyin-project/logs"
mkdir -p "$LOG_DIR"

# 创建生产脚本的包装脚本
cat > /home/jason/aigc-douyin-project/run_daily_production.sh << 'EOF'
#!/bin/bash
# 抖音AIGC新闻视频每日生产执行脚本

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

# 执行生产脚本
echo "执行生产脚本..."
python3 daily_production.py

EXIT_CODE=$?

echo "========================================"
echo "生产脚本执行完成"
echo "退出代码: $EXIT_CODE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

exit $EXIT_CODE
EOF

# 设置执行权限
chmod +x /home/jason/aigc-douyin-project/run_daily_production.sh

# 创建crontab条目
CRON_ENTRY="30 7 * * * /home/jason/aigc-douyin-project/run_daily_production.sh >> /home/jason/aigc-douyin-project/logs/daily_production_$(date +\%Y\%m\%d).log 2>&1"

# 检查是否已存在该任务
if crontab -l 2>/dev/null | grep -q "run_daily_production.sh"; then
    echo "定时任务已存在，更新中..."
    # 删除现有条目
    crontab -l 2>/dev/null | grep -v "run_daily_production.sh" | crontab -
fi

# 添加新条目
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "定时任务设置完成！"
echo "当前crontab内容："
crontab -l

echo ""
echo "定时任务详情："
echo "- 执行时间：每天7:30"
echo "- 执行脚本：/home/jason/aigc-douyin-project/run_daily_production.sh"
echo "- 日志文件：/home/jason/aigc-douyin-project/logs/daily_production_YYYYMMDD.log"
echo "- 输出目标：微信 (o9cq80z13fSvscm6uslCFKadS0js@im.wechat)"

echo ""
echo "你可以手动测试定时任务："
echo "1. 直接运行: /home/jason/aigc-douyin-project/run_daily_production.sh"
echo "2. 查看日志: tail -f /home/jason/aigc-douyin-project/logs/daily_production_$(date +%Y%m%d).log"
echo "3. 查看所有定时任务: crontab -l"