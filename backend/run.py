"""
后端启动脚本 - 在 PyCharm 中直接运行此文件启动后端服务
"""
import sys
import os

# 确保 backend 目录在 Python 路径中，解决 ModuleNotFoundError
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
