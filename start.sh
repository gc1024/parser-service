#!/bin/bash

# Parser Service 启动脚本
# 用于启动 Docker 基础设施 + 本地 Python 服务

set -e

echo "=========================================="
echo "  Parser Service - RAGFlow Core"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 未安装 Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: 未安装 docker-compose${NC}"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}未找到 .env 文件，从 .env.example 复制...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}请编辑 .env 文件配置你的环境变量${NC}"
fi

# 解析命令行参数
COMMAND=${1:-"up"}

case $COMMAND in
    up)
        echo -e "${GREEN}启动 Docker 基础设施...${NC}"
        docker-compose up -d

        echo ""
        echo -e "${GREEN}等待服务就绪...${NC}"
        echo "MySQL 启动中..."
        docker-compose wait mysql
        echo "Redis 启动中..."
        docker-compose wait redis
        echo "Elasticsearch 启动中..."
        docker-compose wait elasticsearch
        echo "MinIO 启动中..."
        docker-compose wait minio

        echo ""
        echo -e "${GREEN}✓ Docker 基础设施已启动${NC}"
        echo ""
        echo -e "${GREEN}服务地址:${NC}"
        echo "  - MySQL:      localhost:3306"
        echo "  - Redis:      localhost:6379"
        echo "  - Elasticsearch: http://localhost:9200"
        echo "  - MinIO API:  http://localhost:9000"
        echo "  - MinIO Console: http://localhost:9001"
        echo ""
        echo -e "${YELLOW}接下来运行以下命令启动 Python 服务:${NC}"
        echo "  ./start.sh python"
        ;;

    python)
        echo -e "${GREEN}启动 Python Parser Service...${NC}"
        echo ""

        # 检查虚拟环境
        if [ ! -d .venv ]; then
            echo -e "${YELLOW}创建虚拟环境...${NC}"
            python3 -m venv .venv
        fi

        # 激活虚拟环境
        source .venv/bin/activate

        # 安装依赖
        echo -e "${YELLOW}检查/安装依赖...${NC}"
        pip install -q -r requirements.txt

        # 启动服务
        echo ""
        echo -e "${GREEN}启动服务 (http://0.0.0.0:9380)...${NC}"
        echo ""
        python main.py
        ;;

    down)
        echo -e "${YELLOW}停止 Docker 基础设施...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ 已停止${NC}"
        ;;

    restart)
        $0 down
        sleep 2
        $0 up
        ;;

    logs)
        docker-compose logs -f ${2:-}
        ;;

    status)
        docker-compose ps
        ;;

    init-db)
        echo -e "${GREEN}初始化数据库...${NC}"
        source .venv/bin/activate
        python main.py --init-superuser
        ;;

    *)
        echo "用法: $0 {up|python|down|restart|logs|status|init-db}"
        echo ""
        echo "命令:"
        echo "  up        - 启动 Docker 基础设施（MySQL, Redis, ES, MinIO）"
        echo "  python    - 启动 Python Parser Service"
        echo "  down      - 停止所有服务"
        echo "  restart   - 重启所有服务"
        echo "  logs      - 查看日志 (可指定服务名)"
        echo "  status    - 查看服务状态"
        echo "  init-db   - 初始化数据库（创建超级用户）"
        echo ""
        echo "示例:"
        echo "  $0 up           # 先启动基础设施"
        echo "  $0 python       # 再启动 Python 服务"
        echo "  $0 logs mysql   # 查看 MySQL 日志"
        exit 1
        ;;
esac
