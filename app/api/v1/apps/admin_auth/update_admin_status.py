from flask import current_app
from flask_restful import Resource
from time import time

from app.api.common import error_code
from app.api.common.parser import admin_status_update_parser  # 导入新定义的 parser
from app.api.common.response import error, success
from app.models.admin import Admin
from app.models import db
# 引入权限控制
from app.utils.decorators import admin_required


class UpdateAdminStatus(Resource):

    method_decorators = [admin_required]

    def post(self):
        """修改管理员状态"""
        
        # 1. 使用封装好的解析器获取参数
        args = admin_status_update_parser()
        admin_id = args.get('admin_id')
        new_status = args.get('status')

        # 2. 验证状态值合法性
        if new_status not in ['0', '1', '2']:
            return error(msg='状态值不合法，仅支持 0(待审核), 1(已通过), 2(已失效)')

        # 3. 查询管理员
        admin = Admin.query.filter_by(admin_id=admin_id).first()
        if not admin:
            return error(msg='管理员不存在')

        # 4. 如果状态未变更，直接返回成功
        if admin.status == new_status:
            return success(msg='状态修改成功')

        # 5. 执行修改逻辑
        try:
            current_timestamp = int(time())
            admin.status = new_status
            admin.update_time = current_timestamp

            # 特殊逻辑：状态变为"已失效"(2)，记录删除时间
            if new_status == '2':
                admin.delete_time = current_timestamp
                # 如果需要立即踢出用户，可在此调用 admin.delete_auth_token()
            
            # 特殊逻辑：从"已失效"恢复，清空删除时间
            elif admin.delete_time:
                admin.delete_time = None

            db.session.commit()
            
            return success(msg='状态修改成功')

        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return error(msg='修改失败，服务器内部错误')