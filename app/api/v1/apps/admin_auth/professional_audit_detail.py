# -*- coding: utf-8 -*-
from flask import g
from flask_restful import Resource
from sqlalchemy.orm import joinedload

from app.api.common.response import success, error
from app.api.common.parser import admin_pro_detail_parser
from app.api.common.fields import professional_audit_result_fields
from app.models.professor import ProfessionalInfo
from app.utils.decorators import login_required_admin

class ProfessionalDetailResource(Resource):
    method_decorators = [login_required_admin]

    def get(self):
        """管理员查看专业申请详情"""
        args = admin_pro_detail_parser()
        target_uid = args.get('user_id')

        # 使用 options 加载关系，防止 N+1 查询
        pro_info = ProfessionalInfo.query.filter_by(user_id=target_uid)\
            .options(
                joinedload(ProfessionalInfo.user), 
                joinedload(ProfessionalInfo.auditor)
            ).first()

        if not pro_info:
            return error(msg="未找到该用户的申请资料")

        # 返回成功，data_fileds 会自动解析关联的 user 和 auditor_name
        return success(
            msg="获取详情成功",
            data=pro_info,
            data_fileds=professional_audit_result_fields()
        )