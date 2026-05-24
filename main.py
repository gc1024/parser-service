"""服务入口脚本，启动 uvicorn 服务器"""

import uvicorn

from app.core.config import load_config


def main():
    """加载配置并启动 uvicorn HTTP 服务器"""
    config = load_config()
    uvicorn.run(
        "app.main:create_app",
        host=config.server.host,
        port=config.server.port,
        workers=config.server.workers,
        factory=True,
        reload=True,
    )


if __name__ == "__main__":
    main()
