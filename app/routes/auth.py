from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from app.auth import generate_token, verify_token

# 创建蓝图对象 - 这行必须存在且正确
bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.get_json()

    # 验证输入
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': '缺少必要字段'}), 400

    # 检查用户是否存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 409

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已被注册'}), 409

    try:
        # 创建用户
        user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'student')
        )
        user.set_password(data['password'])

        # 保存到数据库
        db.session.add(user)
        db.session.commit()

        # 生成令牌
        token = generate_token(user.id)

        return jsonify({
            'success': True,
            'message': '注册成功',
            'user': user.to_dict(),
            'token': token
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()

    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'error': '缺少用户名或密码'}), 400

    # 查找用户（支持用户名或邮箱登录）
    user = User.query.filter(
        (User.username == data['username']) |
        (User.email == data['username'])
    ).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401

    # 生成令牌
    token = generate_token(user.id)

    return jsonify({
        'success': True,
        'message': '登录成功',
        'user': user.to_dict(),
        'token': token
    })


@bp.route('/verify', methods=['POST'])
def verify():
    """验证令牌接口"""
    data = request.get_json()
    token = data.get('token') if data else None

    if not token:
        return jsonify({'error': '缺少令牌'}), 400

    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': '令牌无效或已过期'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    return jsonify({
        'success': True,
        'message': '令牌有效',
        'user': user.to_dict()
    })