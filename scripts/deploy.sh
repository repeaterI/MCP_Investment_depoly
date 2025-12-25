#!/bin/bash
# ============================================
# MCP Investment Portfolio 部署脚本
# 适用于华为云 CodeArts Shell 部署
# ============================================
set -e

# ============ 配置区域（可根据需要修改） ============
APP_NAME="portfolio-server"
APP_DIR="/opt/${APP_NAME}"
VENV_DIR="${APP_DIR}/venv"
LOG_DIR="/var/log/${APP_NAME}"
PID_FILE="/var/run/${APP_NAME}.pid"
PORT=${PORT:-8080}
HOST=${HOST:-"0.0.0.0"}
PYTHON_CMD=${PYTHON_CMD:-"python3"}
# ===================================================

echo "=========================================="
echo "  MCP Investment Portfolio 部署脚本"
echo "=========================================="
echo "部署时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "目标目录: ${APP_DIR}"
echo "服务端口: ${PORT}"
echo ""

# 检查 Python 版本
echo "[1/7] 检查 Python 环境..."
if !  command -v ${PYTHON_CMD} &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(${PYTHON_CMD} --version 2>&1)
echo "Python 版本: ${PYTHON_VERSION}"

# 创建必要目录
echo "[2/7] 创建应用目录..."
sudo mkdir -p ${APP_DIR}
sudo mkdir -p ${LOG_DIR}
sudo chown -R $(whoami):$(whoami) ${APP_DIR}
sudo chown -R $(whoami):$(whoami) ${LOG_DIR}

# 停止旧服务
echo "[3/7] 停止旧服务..."
if [ -f ${PID_FILE} ]; then
    OLD_PID=$(cat ${PID_FILE})
    if ps -p ${OLD_PID} > /dev/null 2>&1; then
        echo "停止进程 PID: ${OLD_PID}"
        kill ${OLD_PID} || true
        sleep 3
    fi
    sudo rm -f ${PID_FILE}
fi
# 确保没有残留进程
pkill -f "python.*main.py.*--sse" || true
sleep 2

# 复制文件
echo "[4/7] 复制应用文件..."
# 清理旧文件（保留虚拟环境）
find ${APP_DIR} -maxdepth 1 -type f -delete 2>/dev/null || true
rm -rf ${APP_DIR}/portfolio_server 2>/dev/null || true
rm -rf ${APP_DIR}/dist 2>/dev/null || true

# 复制新文件
cp -r ${WORKSPACE}/main.py ${APP_DIR}/
cp -r ${WORKSPACE}/claude_server.py ${APP_DIR}/
cp -r ${WORKSPACE}/requirements.txt ${APP_DIR}/
cp -r ${WORKSPACE}/setup.py ${APP_DIR}/
cp -r ${WORKSPACE}/portfolio_server ${APP_DIR}/

# 复制构建产物
if [ -d "${WORKSPACE}/dist" ]; then
    cp -r ${WORKSPACE}/dist ${APP_DIR}/
    echo "已复制构建产物 (egg 包)"
fi

# 创建/更新虚拟环境
echo "[5/7] 配置 Python 虚拟环境..."
cd ${APP_DIR}
if [ ! -d "${VENV_DIR}" ]; then
    echo "创建新的虚拟环境..."
    ${PYTHON_CMD} -m venv ${VENV_DIR}
fi
source ${VENV_DIR}/bin/activate

# 安装依赖
echo "[6/7] 安装依赖..."
pip install --upgrade pip setuptools wheel -q
pip install -r requirements.txt -q

# 安装应用（使用 egg 包或开发模式）
if [ -d "${APP_DIR}/dist" ] && ls ${APP_DIR}/dist/*.egg 1> /dev/null 2>&1; then
    echo "安装 egg 包..."
    pip install ${APP_DIR}/dist/*.egg -q
else
    echo "使用开发模式安装..."
    pip install -e . -q
fi

# 启动服务
echo "[7/7] 启动服务..."
cd ${APP_DIR}
nohup ${VENV_DIR}/bin/python main.py --sse --port=${PORT} \
    > ${LOG_DIR}/server.log 2>&1 &
NEW_PID=$! 
echo ${NEW_PID} | sudo tee ${PID_FILE} > /dev/null

# 等待服务启动
sleep 3

# 验证服务状态
if ps -p ${NEW_PID} > /dev/null 2>&1; then
    echo ""
    echo "=========================================="
    echo "  ✅ 部署成功!"
    echo "=========================================="
    echo "服务 PID:     ${NEW_PID}"
    echo "服务地址:    http://${HOST}:${PORT}"
    echo "日志文件:    ${LOG_DIR}/server. log"
    echo "查看日志:    tail -f ${LOG_DIR}/server. log"
    echo "停止服务:    kill \$(cat ${PID_FILE})"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "  ❌ 部署失败!"
    echo "=========================================="
    echo "请检查日志:  ${LOG_DIR}/server.log"
    cat ${LOG_DIR}/server.log
    exit 1
fi