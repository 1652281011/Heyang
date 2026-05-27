# -*- coding: utf-8 -*-
import time
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash
from .base import db, BaseModel 

class User(db.Model, BaseModel):
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, index=True, comment='账号')
    password = db.Column(db.String(500), nullable=False, comment='哈希密码')
    nickname = db.Column(db.String(50), nullable=False, comment='昵称')
    avatar = db.Column(db.String(255), comment='头像地址')
    email = db.Column(db.String(100), unique=True, comment='邮箱')
    bio = db.Column(db.String(255), comment='个人简介')
    tags = db.Column(db.String(255), comment='兴趣标签')
    post_count = db.Column(db.Integer, default=0)
    total_like_count = db.Column(db.Integer, default=0)
    account_status = db.Column(db.String(10), default='1', comment='1正常, 0禁用')
    role_type = db.Column(db.String(20), default='1', comment='1:普通, 2:专业')

    openid = db.Column(db.String(100), unique=True, index=True)

    pro_info = db.relationship(
        'ProfessionalInfo', 
        backref='user_account', 
        uselist=False, 
        foreign_keys='ProfessionalInfo.user_id' # 关键：指定这个关联字段
    )



    @staticmethod
    def get_or_create_by_openid(openid):
        """根据openid获取用户，不存在则创建"""
        user = User.query.filter_by(openid=openid).first()
        if not user:
            # 创建新用户，初始用户名为openid(或随机)，昵称设为默认
            user = User(
                openid=openid,
                username=openid[:15], # 暂时占位，建议后续引导用户绑定手机号
                password=generate_password_hash("default_pwd"), # 随机密码
                nickname=u"微信用户",
                role_type='1',
                c_time=int(time.time()),
                e_time=int(time.time())
            )
            db.session.add(user)
            db.session.commit()
        return user

    # 校验密码
    def check_password(self, password_plain):
        if not self.password:
            return False
        return check_password_hash(self.password, password_plain)

    def _get_redis_token_key(self, app_type):
        return f"{app_type}_{self.id}_auth_token"

    # --- 核心逻辑：生成 Token 并更新登录时间 ---
    def generate_auth_token(self, expiration=86400, app_type='web'):
        from app import redis_store
        
        # 1. 自动更新最近登陆时间 e_time
        self.e_time = int(time.time())
        try:
            db.session.add(self)
            db.session.commit()
            db.session.refresh(self) # 关键：刷新模型，确保 Python 拿到数据库最新的值
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"更新登录时间失败: {e}")

        # 2. 生成加密 Token
        secret = current_app.config.get('SECRET_KEY')
        salt = current_app.config.get('SALT_KEY', 'user-salt')
        s = Serializer(secret_key=secret, salt=salt)
        
        res = s.dumps({'confirm_id': self.id, 'iat': time.time()})
        auth_token = res.decode('utf-8') if isinstance(res, bytes) else res
        
        # 3. 同步到 Redis
        try:
            redis_key = self._get_redis_token_key(app_type)
            redis_store.set(redis_key, auth_token, ex=expiration)
        except Exception as e:
            current_app.logger.error(f"Redis写入失败 [UID:{self.id}]: {e}")
            
        return auth_token

    @staticmethod
    def verify_auth_token(token, app_type='web'):
        from app import redis_store 
        if not token: return None
        s = Serializer(secret_key=current_app.config.get('SECRET_KEY'), salt=current_app.config.get('SALT_KEY', 'user-salt'))
        try:
            data = s.loads(token)
            user_id = data.get('confirm_id')
            saved_token = redis_store.get(f"{app_type}_{user_id}_auth_token")
            if not saved_token: return None
            if (saved_token.decode('utf-8') if isinstance(saved_token, bytes) else saved_token) != token:
                return None
            return User.query.get(user_id)
        except:
            return None
        
    @staticmethod
    def update_password(user_id, old_pwd, new_pwd):
        user = User.query.get(user_id)
        if not user:
            return False, u"用户不存在"
        
        if not user.check_password(old_pwd):
            return False, u"旧密码验证失败"
        
        # 1. 先尝试在数据库修改密码
        try:
            from werkzeug.security import generate_password_hash
            user.password = generate_password_hash(new_pwd)
            user.e_time = int(time.time())
            
            db.session.add(user)
            db.session.commit() # 提交数据库
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"DB Error: {e}")
            return False, u"数据库保存失败"

        # 2. 数据库成功后，再尝试清除 Token (把清除 Token 移出主 try 块)
        # 即使 Redis 挂了，密码也已经改成功了
        try:
            user.delete_auth_token(app_type='web')
        except Exception as e:
            # 仅记录日志，不向用户返回错误
            current_app.logger.error(f"Redis Token 清除失败(但不影响密码修改): {e}")
        
        return True, u"密码修改成功，请重新登录"

    # 标签操作
    def add_tag(self, tag_name):
        if not tag_name: return False
        tag_list = [t.strip() for t in self.tags.split(',') if t.strip()] if self.tags else []
        if tag_name not in tag_list:
            tag_list.append(tag_name)
            self.tags = ",".join(tag_list)
            return True
        return False

    def delete_tag(self, tag_name):
        if not self.tags: return False
        tag_list = [t.strip() for t in self.tags.split(',') if t.strip()]
        if tag_name in tag_list:
            tag_list.remove(tag_name)
            self.tags = ",".join(tag_list) if tag_list else ""
            return True
        return False

    @classmethod
    def create_user(cls, username, nickname, password_plain, role_type="1", email=None):
        try:
            # 基础查重
            if cls.query.filter_by(username=username).first():
                return None, u"该账号已存在"
            if email and cls.query.filter_by(email=email).first():
                return None, u"该邮箱已被注册"

            user = cls(
                username=username, 
                nickname=nickname, 
                role_type=str(role_type), 
                email=email
            )
            user.password = generate_password_hash(password_plain)
            now = int(time.time())
            user.c_time = now
            user.e_time = now
            db.session.add(user)
            db.session.commit()
            return user, u"注册成功"
        except Exception as e:
            db.session.rollback()
            return None, str(e)
        
    @property
    def c_time_format(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.c_time)) if self.c_time else ""

    @property
    def e_time_format(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.e_time)) if self.e_time else ""
    
    @property
    def active_pro_details(self):
        if str(self.role_type) == '2':
            return self.pro_info
        return None

    def to_upd_dict(self):
        import time
        # 统一格式化
        formatted_e_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.e_time)) if self.e_time else ""
        
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "avatar": self.avatar or "",
            "email": self.email or "",
            "bio": self.bio or "",
            "tags": self.tags or "",
            "e_time": formatted_e_time
        }

    def to_dict(self):
        
        registration_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.c_time)) if getattr(self, 'c_time', None) else ""
        
        try:
            last_login_ts = int(self.e_time) if self.e_time else None
            last_login_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_login_ts)) if last_login_ts else ""
        except:
            last_login_date = ""

        return {
            'username': self.username,
            'nickname': self.nickname,
            "post_count": self.post_count,
            "total_likes": self.total_like_count,
            'avatar': self.avatar or "",
            'email': self.email or "",
            'bio': self.bio or "",
            'tags': self.tags or "",
            'e_time': last_login_date,      # 键名改为 e_time 匹配你的要求
            'c_time': registration_date,    # 键名改为 c_time
            'account_status': self.account_status,
            'role_type': self.role_type
        }