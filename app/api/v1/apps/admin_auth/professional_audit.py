# -*- coding: utf-8 -*-
import time
from flask import g, current_app
from flask_restful import Resource

from app.api.common import error_code
from app.api.common.fields import professional_admin_list_fields, professional_audit_result_fields # 使用之前定义的列表字段过滤
from app.api.common.parser import professional_audit_parser
from app.api.common.response import success, error
from app.models.base import db
from app.models.users import User
from app.models.professor import ProfessionalInfo
from app.utils.decorators import login_required_admin

class ProfessionalAuditResource(Resource):
    method_decorators = [login_required_admin]

    def post(self):
        """
        管理员审核专业身份 (记录审核员信息)
        """
        args = professional_audit_parser()
        target_uid = args.get('user_id')
        action = args.get('action') 
        reason = args.get('reason')

        pro_info = ProfessionalInfo.query.filter_by(user_id=target_uid).first()
        if not pro_info:
            return error(error_code.USER_NOT_EXISTS, msg=u"记录不存在")
        
        user = User.query.get(target_uid)
        
        try:
            now = int(time.time())
            pro_info.audit_status = action
            pro_info.audit_time = now
            pro_info.e_time = now
            
            # 【核心修改】记录当前操作的管理员ID
            # g.admin 是在 login_required_admin 装饰器中被赋值的当前登录管理员对象
            pro_info.auditor_id = g.admin.admin_id 

            if action == 1:
                user.role_type = '2'
                pro_info.reject_reason = ""
                msg = u"已批准该专业身份"
            elif action == 2:
                user.role_type = '1'
                pro_info.reject_reason = reason if reason else u"材料不符合要求"
                msg = u"已驳回该专业身份"
            else:
                return error(error_code.PARAMETER_ERROR, msg=u"无效的操作")

            db.session.commit()
            
            # 刷新以加载 auditor 关联对象，确保 fields 能拿到名字
            db.session.refresh(pro_info)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Audit Save Error: {str(e)}")
            return error(error_code.DB_ERROR, msg=u"数据库保存失败")

        return success(
            msg=msg, 
            data=pro_info, 
            data_fileds=professional_audit_result_fields() 
        )