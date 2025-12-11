#!/bin/bash

# 中药方管理系统完整启动脚本

set -e

echo "======================================"
echo "     中药方管理系统启动脚本"
echo "======================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    print_error "Python3 未安装，请先安装 Python3"
    exit 1
fi

print_info "Python版本: $(python3 --version)"

# 检查并安装系统依赖
if ! dpkg -l | grep -q python3-pip; then
    print_warning "正在安装 python3-pip..."
    sudo apt update && sudo apt install python3-pip python3-venv -y
fi

if ! dpkg -l | grep -q python3.12-venv; then
    print_warning "正在安装 python3-venv..."
    sudo apt install python3.12-venv -y
fi

# 进入项目目录
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)
print_info "项目目录: $PROJECT_DIR"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    print_info "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
print_info "激活虚拟环境..."
source venv/bin/activate

# 安装Python依赖
if [ -f "requirements.txt" ]; then
    print_info "安装Python依赖包..."
    pip install -r requirements.txt
    print_success "依赖安装完成"
else
    print_error "未找到 requirements.txt 文件"
    exit 1
fi

# 检查数据库文件
if [ ! -f "prescriptions.db" ]; then
    print_info "首次运行，正在初始化数据库..."
    python3 -c "from app import init_db; init_db()"
    print_success "数据库初始化完成"
else
    print_info "数据库文件已存在"
fi

# 启动应用
print_info "启动Flask应用..."
print_success "应用启动成功！"
echo ""
echo "======================================"
echo "🌿 中药方管理系统已启动"
echo "======================================"
echo "📍 访问地址:"
echo "   - 本地访问: http://localhost:5001"
echo "   - 局域网访问: http://$(hostname -I | awk '{print $1}'):5001"
echo ""
echo "🔧 管理命令:"
echo "   - 查看日志: tail -f app.log"
echo "   - 停止应用: Ctrl+C 或 pkill -f 'python app.py'"
echo ""
echo "📖 主要功能:"
echo "   ✓ 药方管理 (增删改查)"
echo "   ✓ 智能搜索 (关键词高亮)"
echo "   ✓ 分类筛选"
echo "   ✓ 搜索历史"
echo "   ✓ 数据统计"
echo ""
echo "按 Ctrl+C 停止应用"
echo "======================================"

# 启动应用并记录日志
python3 app.py 2>&1 | tee -a app.log