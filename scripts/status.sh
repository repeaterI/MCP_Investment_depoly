#!/bin/bash
# 检查 MCP Portfolio Server 状态

APP_NAME="portfolio-server"
PID_FILE="/var/run/${APP_NAME}.pid"
LOG_DIR="/var/log/${APP_NAME}"
PORT=${PORT:-8080}

echo "=========================================="
echo "  ${APP_NAME} 服务状态"
echo "=========================================="

if [ -f ${PID_FILE} ]; then
    PID=$(cat ${PID_FILE})
    if ps -p ${PID} > /dev/null 2>&1; then
        echo "状态: ✅ 运行中"
        echo "PID:   ${PID}"
        echo ""
        echo "进程信息:"
        ps -p ${PID} -o pid,user,%cpu,%mem,start,command
    else
        echo "状态: ❌ 已停止 (PID 文件存在但进程不存在)"
    fi
else
    # 尝试查找进程
    PIDS=$(pgrep -f "python.*main.py.*--sse" || true)
    if [ -n "${PIDS}" ]; then
        echo "状态: ⚠️ 运行中 (无 PID 文件)"
        echo "PID:   ${PIDS}"
    else
        echo "状态: ❌ 未运行"
    fi
fi

echo ""
echo "端口检查:"
if command -v netstat &> /dev/null; then
    netstat -tlnp 2>/dev/null | grep ":${PORT}" || echo "端口 ${PORT} 未监听"
elif command -v ss &> /dev/null; then
    ss -tlnp | grep ":${PORT}" || echo "端口 ${PORT} 未监听"
fi

echo ""
echo "最近日志 (最后 10 行):"
if [ -f ${LOG_DIR}/server. log ]; then
    tail -10 ${LOG_DIR}/server.log
else
    echo "日志文件不存在"
fi