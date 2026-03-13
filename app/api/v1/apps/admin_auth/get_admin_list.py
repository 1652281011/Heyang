#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_restful import Resource
from app.api.common.parser import admin_search_parser
from app.api.common.response import success
from app.api.common.fields import get_admin_list_fields
from app.models.admin import Admin

class GetAdminList(Resource):

    def get(self):
        """获取管理员列表接口"""
        
        # 1. 解析参数
        args = admin_search_parser()
        keyword = args.get('keyword')
        status = args.get('status')
        page = args.get('page', 1)
        per_page = args.get('per_page', 20)
        
        # 2. 查询列表 (调用 Model 中的静态方法)
        admins, total = Admin.get_admin_list(page, per_page, keyword, status)
        
        # 3. 获取统计信息
        total_count = Admin.query.count()
        active_count = Admin.query.filter_by(status='1').count() # 已通过
        disabled_count = Admin.query.filter_by(status='2').count() # 已失效/拒绝
        wait_count = Admin.query.filter_by(status='0').count()   # 待审核
        
        # 4. 构造返回数据
        # 建议将分页信息折叠进 'pagination' 字段，结构更清晰
        data = {
            'admins': [admin.to_simple_dict() for admin in admins],
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            },
            'stats': {
                'total_count': total_count,
                'active_count': active_count,
                'disabled_count': disabled_count,
                'wait_count': wait_count
            }
        }
        
        # 5. 返回响应
        return success(
            msg='获取成功',
            data=data,
            data_fileds=get_admin_list_fields()
        )