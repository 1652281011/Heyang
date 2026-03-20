# -*- coding: utf-8 -*-
import json
from flask_restful import Resource
from app.api.common.response import success
from app.api.common.parser import audit_list_parser
from app.api.common.fields import audit_list_fields
from app.models.species_audit import SpeciesAudit

class AdminAuditList(Resource):
    

    def get(self):
        """
        获取审核列表接口
        支持分页和状态筛选
        """
        # 1. 解析参数
        args = audit_list_parser()
        page = args['page']
        per_page = args['per_page']
        status = args['status']

        # 2. 构建查询
        query = SpeciesAudit.query

        # 筛选状态 ('all' 表示查看所有，否则按状态码筛选)
        if status != 'all':
            query = query.filter_by(status=int(status))
        
        # 按创建时间倒序排列（最新的在前面）
        query = query.order_by(SpeciesAudit.create_time.desc())

        # 3. 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 4. 数据处理：将数据库中的 JSON 字符串转为 字典对象
        items = []
        for item in pagination.items:
            # 手动构建字典，以便处理 content_snapshot
            temp = {
                'audit_id': item.audit_id,
                'applicant_id': item.applicant_id,
                'operate_type': item.operate_type,
                'target_species_id': item.target_species_id,
                'status': item.status,
                'reject_reason': item.reject_reason,
                'create_time': item.create_time,
                'audit_time': item.audit_time,
                'auditor_id': item.auditor_id,
                'content_snapshot': {} # 默认为空字典
            }
            
            # 解析 JSON
            if item.content_snapshot:
                try:
                    temp['content_snapshot'] = json.loads(item.content_snapshot)
                except Exception:
                    temp['content_snapshot'] = {"error": "数据快照解析失败"}
            
            items.append(temp)

        # 5. 构造返回数据
        data = {
            'audit_list': items,
            'pagination': {
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': (pagination.total + per_page - 1) // per_page
            }
        }
        
        return success(msg='获取成功', data=data, data_fileds=audit_list_fields())