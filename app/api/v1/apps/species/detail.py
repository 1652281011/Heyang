# app/api/species_api.py
from flask import g, request
from flask_restful import Resource, marshal_with
from app.api.common.parser import species_detail_parser
from app.api.common.fields import get_species_detail_fields
from app.api.common.response import error, success
from app.models.species import Species
from app.services.species.species_services import SpeciesService

from app.models.users import User # 导入用户模型

def check_has_advanced_permission(user):
    """
    判定当前用户是否有权查看形态学信息：
    1. 超级管理员 (role_type='9') -> 允许
    2. 普通管理员 (role_type='8') -> 允许
    3. 审核通过的专家 (role_type='2' 且 audit_status=1) -> 允许
    """
    if not user:
        return False

    role_type = str(getattr(user, 'role_type', ''))

    # 1. 如果是管理员 (9 或 8)，直接通过，不需要检查专家表
    if role_type in ['9', '8']:
        return True

    # 2. 如果是专家 (2)，则需要检查审核状态
    if role_type == '2':
        try:
            pro_info = getattr(user, 'pro_info', None)
            if pro_info and getattr(pro_info, 'audit_status', None) == 1:
                return True
        except Exception as e:
            print(f"查询专家表异常: {e}")
            return False

    return False
class GetSpeciesDetail(Resource):
    """
    物种详情：不强制登录，专家可见三维/形态学模块
    """
    def get(self):
        # 1. 解析 species_id
        args = species_detail_parser()
        species_id = args.get('species_id')

        # 2. 获取用户并判定专家身份
        # 假设系统拦截器已将用户对象存入 g.user
        current_user = getattr(g, 'user', None)
        is_expert = check_has_advanced_permission(current_user)
        print(f"DEBUG: Service接收到的is_expert状态为: {is_expert}") 

        # 3. 调用 Service 获取过滤后的数据
        # 内部自动处理了 URL 动态拼接和形态学分类
        data = SpeciesService.get_species_detail(species_id, is_expert=is_expert)

        if not data:
            return error(resid=404, msg='物种信息不存在')

        return success(
            msg='获取成功',
            data=data,
            data_fileds=get_species_detail_fields()
        )