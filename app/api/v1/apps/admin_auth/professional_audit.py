# -*- coding: utf-8 -*-
import time
from flask import g, current_app
from flask_restful import Resource

from app.models import db
from app.models.users import User
from app.models.professor import ProfessionalInfo
from app.api.common.response import success, error
from app.api.common.parser import professional_audit_parser
from app.api.common.fields import professional_audit_result_fields
from app.utils.decorators import admin_required, login_required

class ProfessionalAuditResource(Resource):
    # 允许一般管理员(8)和高级管理员(9)操作
    method_decorators = [admin_required, login_required]

    def post(self):
        """
        管理员审核专业身份
        """
        args = professional_audit_parser()
        target_uid = args.get('user_id')
        action = args.get('action')  # 1: 通过, 2: 驳回
        reason = args.get('reason')

        # 1. 查询申请记录
        pro_info = db.session.query(ProfessionalInfo).filter_by(user_id=target_uid).first()
        if not pro_info:
            return error(msg=u"未找到该用户的申请记录")
        
        # 2. 查询对应的用户账号
        user = db.session.query(User).get(target_uid)
        if not user:
            return error(msg=u"关联用户不存在")
        
        try:
            now = int(time.time())
            pro_info.audit_status = action
            pro_info.audit_time = now
            pro_info.e_time = now
            
            # 【核心修改】使用 g.user.id 记录当前审核的管理员
            # 在你的 before_request 拦截器中，g.user 已经是当前登录的管理员对象
            pro_info.admin_id = g.user.id 

            if str(action) == '1':
                user.role_type = '2'  # 身份变更为“专业人员”
                pro_info.reject_reason = ""
                msg = u"已批准该专业身份申请"
            elif str(action) == '2':
                user.role_type = '1'  # 恢复为“普通用户”
                pro_info.reject_reason = reason if reason else u"材料不符合要求"
                msg = u"已驳回该专业身份申请"
            else:
                return error(msg=u"无效的操作类型")

            db.session.commit()
            
            # 刷新以确保关联的 auditor (管理员) 对象能被 fields 正常解析
            db.session.refresh(pro_info)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Professional Audit Error: {str(e)}")
            return error(msg=u"数据库更新失败")

        return success(
            msg=msg, 
            data=pro_info, 
            data_fileds=professional_audit_result_fields() 
        )