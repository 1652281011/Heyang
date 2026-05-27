# -*- coding: utf-8 -*-
from flask_restful import Resource
from sqlalchemy import or_
from sqlalchemy.orm import contains_eager

from app.models import db
from app.models.users import User
from app.models.professor import ProfessionalInfo
from app.api.common.parser import professional_list_parser
from app.api.common.fields import professional_admin_list_fields
from app.api.common.response import success
from app.utils.decorators import admin_required, login_required


class ProfessionalListResource(Resource):
    method_decorators = [admin_required, login_required]

    def get(self):
        """
        管理员获取专业身份申请列表 (含搜索和分页)
        """
        args = professional_list_parser()
        
        page = args.get('page', 1)
        per_page = min(args.get('per_page', 10), 50)
        status = args.get('status')
        search = args.get('search')

        # 1. 基础查询：使用 db.session.query
        # 关联 user_account (即申请人账号)
        query = db.session.query(ProfessionalInfo).join(ProfessionalInfo.user_account)

        # 2. 状态筛选
        if status is not None:
            query = query.filter(ProfessionalInfo.audit_status == status)

        # 3. 动态搜索
        if search:
            query = query.filter(or_(
                User.nickname.like(f'%{search}%'),
                User.username.like(f'%{search}%'),
                ProfessionalInfo.real_name.like(f'%{search}%')
            ))

        # 4. 分页与排序
        # contains_eager 确保 user_account 数据被一次性查出，解决歧义外键后的 N+1 问题
        pagination = query.options(contains_eager(ProfessionalInfo.user_account)) \
                          .order_by(ProfessionalInfo.c_time.desc()) \
                          .paginate(page=page, per_page=per_page, error_out=False)

        # 5. 组装符合你前端要求的数据结构
        formatted_data = {
            "species_list": pagination.items,  # 沿用之前的 key 名，或者改为 pro_list
            "pagination": {
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "pages": pagination.pages
            }
        }

        return success(
            msg=u"获取申请列表成功",
            data=formatted_data,
            data_fileds=professional_admin_list_fields()
        )