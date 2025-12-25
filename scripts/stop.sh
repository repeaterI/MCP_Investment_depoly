#!/bin/bash
# 停止 MCP Portfolio Server
set -e

APP_NAME="portfolio-server"
PID_FILE="/var/run/${APP_NAME}.pid"

echo "停止 ${APP_NAME}..."

if [ -f ${PID_FILE} ]; then
    PID=$(cat ${PID_FILE})
    if ps -p ${PID} > /dev/null 2>&1; then
        kill ${PID}
        echo "已停止进程 PID:  ${PID}"
    else
        echo "进程 ${PID} 不存在"
    fi
    sudo rm -f ${PID_FILE}
else
    echo "PID 文件不存在，尝试查找进程..."
    pkill -f "python.*main.py.*--sse" || echo "未找到运行中的服务"
fi

echo "服务已停止"