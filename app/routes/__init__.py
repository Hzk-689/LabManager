# 导入配置类
from config import Config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# 创建数据库实例
db = SQLAlchemy()


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    CORS(app)  # 启用跨域支持

    # 注册蓝图（路由）
    try:
        from app.routes.main import bp as main_bp
        app.register_blueprint(main_bp)
        print("✅ 主路由蓝图注册成功")
    except ImportError as e:
        print(f"⚠️ 主路由蓝图注册失败: {e}")

    try:
        from app.routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp)
        print("✅ 认证路由蓝图注册成功")
    except ImportError as e:
        print(f"⚠️ 认证路由蓝图注册失败: {e}")

    # 关键修复：导入模型，确保它们被注册到数据库元数据
    # 在 create_app 函数中
    try:
        from app.routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp)
        print("✅ 认证蓝图注册成功")
    except Exception as e:
        print(f"❌ 认证蓝图注册失败: {e}")
        import traceback
        traceback.print_exc()  # 打印详细错误信息
    return app