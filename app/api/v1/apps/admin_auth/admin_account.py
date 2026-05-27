from flask import request
from flask_restful import Resource
from app.api.common.fields import get_admin_user_fields
from app.api.common.response import success, error
from app.models.users import User
from app.models import db

from werkzeug.security import generate_password_hash
import time

from app.utils.decorators import login_required, super_admin_required

class AdminAccountManage(Resource):
    method_decorators = [super_admin_required, login_required]

    def get(self):
        """获取所有一般管理员列表"""
        admins = User.query.filter_by(role_type='8').all()
        return success(msg='获取成功', data=admins, data_fileds=get_admin_user_fields())

    def post(self):
        data = request.get_json()
        username = data.get('username')
        nickname = data.get('nickname', u'一般管理员')

        if not username:
            return error(resid=400, msg='账号名（手机号）不能为空')

        if User.query.filter_by(username=username).first():
            return error(resid=100, msg='该账号已存在')

        initial_password = generate_password_hash('123456')

        new_admin = User(
            username=username,
            password=initial_password,
            nickname=nickname,
            role_type='8',      # 一般管理员标识
            account_status='1', # 默认正常
            c_time=int(time.time()),
        )

        try:
            db.session.add(new_admin)
            db.session.commit()
            return success(msg='管理员创建成功，初始密码为123456')
        except Exception as e:
            db.session.rollback()
            return error(resid=500, msg='服务器写入失败')

    def delete(self):
        """删除一般管理员"""
        admin_id = request.args.get('id')
        target = User.query.filter_by(id=admin_id, role_type='8').first()
        
        if not target:
            return error(resid=404, msg='未找到该管理员')

        try:
            # 不直接 delete，而是修改状态
            target.account_status = '0'  # 假设 0 代表禁用
            # 或者修改 role_type 使其失去管理员权限
            # target.role_type = '1' 
            
            db.session.commit()
            return success(msg='该管理员账号已禁用')
        except Exception as e:
            db.session.rollback()
            return error(resid=500, msg='操作失败')