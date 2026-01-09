import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 密钥，用于保护会话等
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-replace-me-in-production'

    # 数据库配置（SQLite）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False