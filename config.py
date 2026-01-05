import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 密钥，用于保护会话等，可随意设置一个复杂字符串
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-replace-me'
    
    # 数据库配置（我们先使用SQLite，无需安装，后期可换MySQL）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭警告信息