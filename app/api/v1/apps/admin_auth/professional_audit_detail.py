# -*- coding: utf-8 -*-
from flask import g
from flask_restful import Resource
from sqlalchemy.orm import joinedload

from app.models import db
from app.api.common.response import success, error
from app.api.common.parser import admin_pro_detail_parser
from app.api.common.fields import professional_audit_result_fields
from app.models.professor import ProfessionalInfo
from app.utils.decorators import admin_required, login_required

class ProfessionalDetailResource(Resource):
    # 只要是管理员（Role 8 或 9）且已登录，就可以查看申请详情
    method_decorators = [admin_required, login_required]

    def get(self):
        """管理员查看专家申请详情"""
        # 1. 获取参数（待查看的专家用户ID）
        args = admin_pro_detail_parser()
        target_uid = args.get('user_id')

        if not target_uid:
            return error(msg="缺少用户ID参数")

        # 2. 数据库查询
        # 注意：这里的 joinedload 内部名称必须与你在 ProfessionalInfo 模型中定义的字段名一致
        # 假设：
        # - 专家本人的关系名叫 'user_account' (对应 user_id)
        # - 审核管理员的关系名叫 'auditor' (对应 admin_id)
        try:
            pro_info = db.session.query(ProfessionalInfo).filter_by(user_id=target_uid)\
                .options(
                    joinedload(ProfessionalInfo.user_account), # 获取专家账号基本信息
                    joinedload(ProfessionalInfo.auditor)       # 获取审核人基本信息
                ).first()
        except Exception as e:
            # 调试：如果 relationship 名字写错，这里会报错
            print(f"Query Error: {str(e)}")
            pro_info = db.session.query(ProfessionalInfo).filter_by(user_id=target_uid).first()

        if not pro_info:
            return error(msg="未找到该用户的申请资料")

        # 3. 返回数据
        # 这里的 pro_info 对象会传入 professional_audit_result_fields 进行 marshal 格式化
        return success(
            msg="获取详情成功",
            data=pro_info,
            data_fileds=professional_audit_result_fields()
        )