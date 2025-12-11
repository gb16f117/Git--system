#!/bin/bash

# 中药方管理系统启动脚本

echo "=== 中药方管理系统启动脚本 ==="

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "检查并安装依赖..."
pip install -r requirements.txt

# 启动应用
echo "启动应用..."
echo "访问地址: http://localhost:5001"
echo "按 Ctrl+C 停止应用"
echo ""

python3 app.py