# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource
from sqlalchemy.orm import joinedload
from app.api.common.response import success, error
from app.api.common.parser import species_post_detail_parser
from app.api.common.fields import get_ident_detail_fields
from app.models.identification import SpeciesPost
from app.models.users import User

class SpeciesPostDetail(Resource):
    def get(self):
        """
        获取帖子详情
        允许游客访问；若提供 Auth-Token，则附带 my_vote_id
        """
        # 1. 尝试解析当前用户 (不强制拦截)
        auth_token = request.headers.get('Auth-Token')
        current_user = User.verify_auth_token(auth_token) if auth_token else None

        # 2. 获取参数
        args = species_post_detail_parser()
        post_id = args['post_id']

        try:
            # 3. 查询帖子，并使用 joinedload 预加载关联数据，防止 N+1 性能问题
            post = SpeciesPost.query.options(
                joinedload(SpeciesPost.author),                # 发帖人信息
                joinedload(SpeciesPost.candidates),            # 候选标签
                joinedload(SpeciesPost.expert).joinedload(User.pro_info) # 专家及其专业身份
            ).filter_by(id=post_id).first()

            if not post:
                return error(msg='该鉴定贴不存在或已被删除')

            # 4. 动态计算当前用户的投票状态
            uid = current_user.id if current_user else None
            post.my_vote_id = post.get_user_vote_id(uid)

            # 5. 格式化并返回
            return success(
                msg='获取详情成功', 
                data=post, 
                data_fileds=get_ident_detail_fields()
            )

        except Exception as e:
            return error(msg=f"获取详情失败: {str(e)}")