# -*- coding: utf-8 -*-
from flask_restful import Resource, marshal_with
from sqlalchemy import or_
from sqlalchemy.orm import contains_eager

from app.models.base import db
from app.models.users import User
from app.models.professor import ProfessionalInfo
from app.api.common.parser import professional_list_parser
from app.api.common.fields import professional_admin_list_fields
from app.utils.decorators import login_required_admin

class ProfessionalListResource(Resource):
    method_decorators = [login_required_admin]

    @marshal_with(professional_admin_list_fields())
    def get(self):
        """
        管理员获取专业身份申请全列表
        """
        args = professional_list_parser()
        
        # 参数获取与安全限制
        page = args.get('page', 1)
        per_page = min(args.get('per_page', 10), 50)
        status = args.get('status')
        search = args.get('search')

        # 1. 基础查询：显式 JOIN User 表
        query = ProfessionalInfo.query.join(ProfessionalInfo.user)

        # 2. 动态筛选状态 (0, 1, 2)
        if status is not None:
            query = query.filter(ProfessionalInfo.audit_status == status)

        # 3. 动态搜索 (跨表多字段模糊匹配)
        if search:
            query = query.filter(or_(
                User.nickname.like(f'%{search}%'),
                User.username.like(f'%{search}%'),
                ProfessionalInfo.real_name.like(f'%{search}%')
            ))

        # 4. 分页与排序 (利用 contains_eager 优化 N+1 问题)
        # contains_eager 告诉 SQLAlchemy 用户表的数据已经在 JOIN 结果里了，直接取
        pagination = query.options(contains_eager(ProfessionalInfo.user)) \
                          .order_by(ProfessionalInfo.c_time.desc()) \
                          .paginate(page=page, per_page=per_page, error_out=False)

        # 5. 返回符合 marshal_with 结构的字典
        return {
            "resid": 200,
            "msg": "获取列表成功",
            "status": "success",
            "data": {
                "list": pagination.items,
                "total": pagination.total,
                "page": page,
                "per_page": per_page
            }
        }