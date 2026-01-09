from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app


class User(db.Model):
    """用户表 - 管理系统用户账户"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系：用户发起的预约
    reservations_as_applicant = db.relationship(
        'Reservation',
        foreign_keys='Reservation.user_id',
        backref='applicant_user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # 关系：用户审核的预约
    reservations_as_reviewer = db.relationship(
        'Reservation',
        foreign_keys='Reservation.reviewed_by',
        backref='reviewer_user',
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role in ['admin', 'super']

    def generate_auth_token(self, expires_in=3600):
        """生成JWT令牌"""
        from app.auth import generate_token
        return generate_token(self.id, expires_in)

    @staticmethod
    def verify_auth_token(token):
        """验证JWT令牌并返回用户对象"""
        from app.auth import verify_token
        user_id = verify_token(token)
        if user_id is None:
            return None
        return User.query.get(user_id)

    def to_dict(self):
        """将用户信息转为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
class Device(db.Model):
    """实验室设备表"""
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    # 设备基本信息
    device_id = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='设备编号')
    name = db.Column(db.String(100), nullable=False, comment='设备名称')
    device_type = db.Column(db.String(50), nullable=False, comment='设备类型')
    brand = db.Column(db.String(50), comment='品牌')
    model = db.Column(db.String(50), comment='型号')

    # 设备状态管理
    status = db.Column(db.String(20), default='available', nullable=False,
                       comment='设备状态：available(可用), reserved(已预约), in_use(使用中), maintenance(维修中)')
    location = db.Column(db.String(100), comment='存放位置')

    # 设备规格与描述
    specifications = db.Column(db.Text, comment='规格参数')
    description = db.Column(db.Text, comment='设备描述')

    # 使用统计
    total_usage_hours = db.Column(db.Float, default=0.0, comment='累计使用时长(小时)')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='入库时间')
    last_maintenance = db.Column(db.DateTime, comment='上次维护时间')

    # 关系：一个设备可以有多条预约记录
    # 明确指定使用 Reservation.device_id 外键
    reservations = db.relationship(
        'Reservation',
        foreign_keys='[Reservation.device_id]',
        backref='device_info',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Device {self.device_id}: {self.name}>'

    def to_dict(self):
        """将设备信息转为字典，便于API返回"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'type': self.device_type,
            'status': self.status,
            'location': self.location,
            'total_usage_hours': self.total_usage_hours
        }


class Reservation(db.Model):
    """设备预约记录表"""
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)

    # 外键关联：预约的用户
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='预约用户ID')

    # 外键关联：被预约的设备
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, comment='预约设备ID')

    # 预约时间信息
    start_time = db.Column(db.DateTime, nullable=False, comment='预约开始时间')
    end_time = db.Column(db.DateTime, nullable=False, comment='预约结束时间')

    # 预约详情
    purpose = db.Column(db.Text, nullable=False, comment='预约用途说明')
    status = db.Column(db.String(20), default='pending', nullable=False,
                       comment='预约状态: pending(待审核), approved(已批准), rejected(已拒绝), in_use(使用中), completed(已完成), cancelled(已取消)')

    # 管理员相关字段
    admin_notes = db.Column(db.Text, comment='管理员审批意见')
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='审核管理员ID')
    reviewed_at = db.Column(db.DateTime, comment='审核时间')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def __repr__(self):
        return f'<Reservation {self.id}: User{self.user_id} -> Device{self.device_id}>'

    def to_dict(self):
        """将预约信息转为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'purpose': self.purpose,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def check_time_conflict(self, other_start, other_end):
        """检查时间冲突的算法（重要！）"""
        # 核心算法：判断两个时间段是否有重叠
        return (self.start_time < other_end) and (self.end_time > other_start)