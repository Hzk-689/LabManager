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
    CORS(app)

    # 注册蓝图 - 先注册主蓝图
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    # 注册认证蓝图
    try:
        from app.routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp)
        print("✅ 认证蓝图注册成功")
    except Exception as e:
        print(f"❌ 认证蓝图注册失败: {e}")
        import traceback
        traceback.print_exc()

    # 导入模型
    from app import models

    return app