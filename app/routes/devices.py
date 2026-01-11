from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Device, User
from app.auth import verify_token
from functools import wraps
import datetime

bp = Blueprint('devices', __name__, url_prefix='/api/devices')


# ==================== 权限验证装饰器 ====================

def token_required(f):
    """验证JWT令牌的装饰器"""

    @wraps(f)
    def decorated(*args, **kwargs):
        # 从请求头获取令牌
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': '缺少认证令牌'}), 401

        # 解析Bearer令牌
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': '令牌格式错误，应为: Bearer <token>'}), 401

        token = parts[1]
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': '令牌无效或已过期'}), 401

        # 获取用户并添加到请求上下文
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 将用户对象传递给被装饰的函数
        return f(user, *args, **kwargs)

    return decorated


def admin_required(f):
    """验证管理员权限的装饰器"""

    @wraps(f)
    def decorated(user, *args, **kwargs):
        if not user.is_admin():
            return jsonify({'error': '需要管理员权限'}), 403
        return f(user, *args, **kwargs)

    return decorated


# ==================== 设备API接口 ====================

@bp.route('/', methods=['GET'])
@token_required
def get_devices(user):
    """获取设备列表（支持分页、筛选、搜索）"""
    try:
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # 筛选参数
        status = request.args.get('status')
        device_type = request.args.get('type')
        category = request.args.get('category')
        location = request.args.get('location')
        search = request.args.get('search')

        # 构建查询
        query = Device.query

        # 应用筛选条件
        if status:
            query = query.filter(Device.status == status)
        if device_type:
            query = query.filter(Device.device_type == device_type)
        if category:
            query = query.filter(Device.category == category)
        if location:
            query = query.filter(Device.location.contains(location))
        if search:
            # 多字段搜索
            search_pattern = f'%{search}%'
            query = query.filter(
                (Device.name.ilike(search_pattern)) |
                (Device.device_id.ilike(search_pattern)) |
                (Device.description.ilike(search_pattern))
            )

        # 排序（默认按创建时间倒序）
        query = query.order_by(Device.created_at.desc())

        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        devices = pagination.items

        return jsonify({
            'success': True,
            'data': [device.to_dict() for device in devices],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            },
            'filters': {
                'status': status,
                'type': device_type,
                'category': category,
                'location': location,
                'search': search
            }
        })

    except Exception as e:
        current_app.logger.error(f'获取设备列表失败: {e}')
        return jsonify({'success': False, 'error': '获取设备列表失败'}), 500


@bp.route('/<int:device_id>', methods=['GET'])
@token_required
def get_device(user, device_id):
    """获取单个设备详情"""
    try:
        device = Device.query.get_or_404(device_id)
        return jsonify({
            'success': True,
            'data': device.to_dict(detail=True)
        })
    except Exception as e:
        current_app.logger.error(f'获取设备详情失败: {e}')
        return jsonify({'success': False, 'error': '设备不存在'}), 404


@bp.route('/', methods=['POST'])
@token_required
@admin_required
def create_device(user):
    """创建设备（管理员权限）"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400

        # 验证必要字段
        required_fields = ['device_id', 'name', 'device_type']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'success': False, 'error': f'缺少必要字段: {", ".join(missing_fields)}'}), 400

        # 检查设备ID是否已存在
        if Device.query.filter_by(device_id=data['device_id']).first():
            return jsonify({'success': False, 'error': '设备编号已存在'}), 409

        # 创建设备对象
        device = Device()

        # 设置基本字段
        device.device_id = data['device_id']
        device.name = data['name']
        device.device_type = data['device_type']

        # 设置可选字段
        optional_fields = [
            'category', 'brand', 'model', 'serial_number', 'status',
            'location', 'lab_room', 'specifications', 'description',
            'purchase_date', 'warranty_period', 'maintenance_interval',
            'responsible_person', 'contact_info', 'is_shared', 'max_reservation_hours'
        ]

        for field in optional_fields:
            if field in data:
                setattr(device, field, data[field])

        # 处理技术参数（JSON字段）
        if 'technical_parameters' in data and data['technical_parameters']:
            device.technical_parameters = data['technical_parameters']

        # 处理日期字段
        date_fields = ['purchase_date', 'last_maintenance']
        for date_field in date_fields:
            if date_field in data and data[date_field]:
                try:
                    setattr(device, date_field,
                            datetime.datetime.fromisoformat(data[date_field].replace('Z', '+00:00')))
                except ValueError:
                    return jsonify({'success': False, 'error': f'{date_field}日期格式错误，应为ISO格式'}), 400

        # 保存到数据库
        db.session.add(device)
        db.session.commit()

        current_app.logger.info(f'管理员 {user.username} 创建设备: {device.device_id}')

        return jsonify({
            'success': True,
            'message': '设备创建成功',
            'data': device.to_dict(detail=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'创建设备失败: {e}')
        return jsonify({'success': False, 'error': '创建设备失败'}), 500


@bp.route('/<int:device_id>', methods=['PUT'])
@token_required
@admin_required
def update_device(user, device_id):
    """更新设备信息（管理员权限）"""
    try:
        device = Device.query.get_or_404(device_id)
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400

        # 检查设备ID是否重复（如果修改了device_id）
        if 'device_id' in data and data['device_id'] != device.device_id:
            if Device.query.filter_by(device_id=data['device_id']).first():
                return jsonify({'success': False, 'error': '设备编号已存在'}), 409

        # 更新字段
        updatable_fields = [
            'device_id', 'name', 'device_type', 'category', 'brand', 'model',
            'serial_number', 'status', 'location', 'lab_room', 'specifications',
            'description', 'purchase_date', 'warranty_period', 'maintenance_interval',
            'responsible_person', 'contact_info', 'is_shared', 'max_reservation_hours',
            'qr_code'
        ]

        for field in updatable_fields:
            if field in data:
                setattr(device, field, data[field])

        # 处理技术参数
        if 'technical_parameters' in data:
            device.technical_parameters = data['technical_parameters']

        # 处理日期字段
        date_fields = ['purchase_date', 'last_maintenance', 'next_maintenance']
        for date_field in date_fields:
            if date_field in data and data[date_field] is not None:
                try:
                    if data[date_field]:  # 非空字符串
                        setattr(device, date_field,
                                datetime.datetime.fromisoformat(data[date_field].replace('Z', '+00:00')))
                    else:  # 空字符串表示清空
                        setattr(device, date_field, None)
                except ValueError:
                    return jsonify({'success': False, 'error': f'{date_field}日期格式错误，应为ISO格式'}), 400

        # 保存更新
        db.session.commit()

        current_app.logger.info(f'管理员 {user.username} 更新设备: {device.device_id}')

        return jsonify({
            'success': True,
            'message': '设备更新成功',
            'data': device.to_dict(detail=True)
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'更新设备失败: {e}')
        return jsonify({'success': False, 'error': '更新设备失败'}), 500


@bp.route('/<int:device_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_device(user, device_id):
    """删除设备（管理员权限）"""
    try:
        device = Device.query.get_or_404(device_id)

        # 检查是否有相关预约
        if device.reservations.count() > 0:
            return jsonify({'success': False, 'error': '设备存在相关预约，无法删除'}), 400

        # 删除设备
        db.session.delete(device)
        db.session.commit()

        current_app.logger.info(f'管理员 {user.username} 删除设备: {device.device_id}')

        return jsonify({
            'success': True,
            'message': '设备删除成功'
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'删除设备失败: {e}')
        return jsonify({'success': False, 'error': '删除设备失败'}), 500


@bp.route('/<int:device_id>/status', methods=['PUT'])
@token_required
@admin_required
def update_device_status(user, device_id):
    """更新设备状态（管理员权限）"""
    try:
        device = Device.query.get_or_404(device_id)
        data = request.get_json()

        if not data or 'status' not in data:
            return jsonify({'success': False, 'error': '缺少状态字段'}), 400

        new_status = data['status']

        # 更新状态
        device.update_status(new_status)
        db.session.commit()

        current_app.logger.info(f'管理员 {user.username} 更新设备状态: {device.device_id} -> {new_status}')

        return jsonify({
            'success': True,
            'message': f'设备状态已更新为 {new_status}',
            'data': device.to_dict()
        })

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'更新设备状态失败: {e}')
        return jsonify({'success': False, 'error': '更新设备状态失败'}), 500


@bp.route('/<int:device_id>/usage', methods=['POST'])
@token_required
def record_device_usage(user, device_id):
    """记录设备使用时长"""
    try:
        device = Device.query.get_or_404(device_id)
        data = request.get_json()

        if not data or 'hours' not in data:
            return jsonify({'success': False, 'error': '缺少使用时长字段'}), 400

        hours = float(data['hours'])

        # 记录使用时长
        device.record_usage(hours)
        db.session.commit()

        current_app.logger.info(f'用户 {user.username} 记录设备使用: {device.device_id} {hours}小时')

        return jsonify({
            'success': True,
            'message': f'已记录{hours}小时使用时长',
            'data': device.to_dict()
        })

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'记录设备使用失败: {e}')
        return jsonify({'success': False, 'error': '记录设备使用失败'}), 500