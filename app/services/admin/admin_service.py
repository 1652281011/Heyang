import time
from app.models import db
from app.models.users import User
from werkzeug.security import generate_password_hash


class AdminService:
    
    @staticmethod
    def get_admin_list():
        """获取所有一般管理员列表"""
        # 只查询 role_type 为 8 的账号
        admins = db.session.query(User).filter_by(role_type=8).all()
        return [admin.to_dict() for admin in admins]

    @staticmethod
    def add_general_admin(username, password, real_name):
        """新增一般管理员"""
        # 检查账号名是否存在
        exists = db.session.query(User).filter_by(username=username).first()
        if exists:
            return False, "该账号已存在"
        
        new_admin = User(
            username=username,
            password=generate_password_hash(password), # 密码哈希加密
            real_name=real_name,
            role_type=8, # 固定为一般管理员
            c_time=int(time.time())
        )
        db.session.add(new_admin)
        db.session.commit()
        return True, new_admin.user_id

    @staticmethod
    def delete_admin(admin_id):
        """删除管理员账号"""
        admin = db.session.query(User).filter_by(user_id=admin_id, role_type=8).first()
        if not admin:
            return False, "未找到该一般管理员账号"
        
        db.session.delete(admin)
        db.session.commit()
        return True, "删除成功"