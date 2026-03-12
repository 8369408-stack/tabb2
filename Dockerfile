FROM python:3.11-slim

LABEL maintainer="Tabbit2API"
LABEL description="Tabbit2API - Tabbit to OpenAI/Claude Compatible API"

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

WORKDIR /app

# 安装依赖（利用 Docker 缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 清理不必要的文件 & 设置脚本权限
RUN rm -rf __pycache__ core/__pycache__ routes/__pycache__ \
    && find . -name "*.pyc" -delete \
    && chmod +x docker-entrypoint.sh

# 数据卷：持久化配置文件
VOLUME ["/app/data"]

# 暴露默认端口
EXPOSE 8800

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8800/v1/models')" || exit 1

# 使用 entrypoint 脚本启动
ENTRYPOINT ["./docker-entrypoint.sh"]
