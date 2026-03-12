#!/bin/bash
set -e

CONFIG_FILE="/app/data/config.json"
APP_CONFIG="/app/config.json"

# 如果 data 目录下有配置文件，则软链接到应用目录
if [ -f "$CONFIG_FILE" ]; then
    echo "[Entrypoint] 使用已有配置: $CONFIG_FILE"
    ln -sf "$CONFIG_FILE" "$APP_CONFIG"
elif [ -f "$APP_CONFIG" ]; then
    # 首次启动：将已有配置迁移到 data 目录
    echo "[Entrypoint] 迁移配置到持久化目录..."
    mkdir -p /app/data
    cp "$APP_CONFIG" "$CONFIG_FILE"
    ln -sf "$CONFIG_FILE" "$APP_CONFIG"
else
    # 全新安装：应用启动时会自动生成 config.json
    echo "[Entrypoint] 首次启动，将自动生成配置文件..."
    mkdir -p /app/data
    # 创建软链接，让应用生成的配置直接写入 data 目录
    ln -sf "$CONFIG_FILE" "$APP_CONFIG"
fi

echo "[Entrypoint] 启动 Tabbit2API..."
exec python tabbit2api.py
