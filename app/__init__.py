from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    # 修改这里：从app.routes导入main_bp
    from app.routes import main_bp
    app.register_blueprint(main_bp)  # 注册蓝图
    
    return app