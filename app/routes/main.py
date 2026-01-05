from flask import Blueprint, jsonify

# 这里必须创建 Blueprint 实例
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return jsonify({'message': '欢迎来到实验室设备管理系统后端API！'})

@bp.route('/api/test')
def test():
    return jsonify({'status': 'success', 'data': '后端服务连接测试成功！'})