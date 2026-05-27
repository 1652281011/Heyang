# -*- coding: utf-8 -*-
import time
from flask import g, request
from flask_restful import Resource
from app.api.common.fields import get_expert_confirm_res_fields
from app.api.common.parser import species_expert_confirm_parser
from app.models.base import db

from app.api.common.response import error, success
from app.models.identification import SpeciesCandidate, SpeciesPost
from app.utils.decorators import expert_required, login_required
class ExpertConfirmAction(Resource):
    method_decorators = [expert_required]

    def post(self):
        """
        专家鉴定接口：支持多次鉴定（覆盖上一次结果）
        """
        args = species_expert_confirm_parser()
        post_id = args['post_id']
        cand_id = args['candidate_id']
        opinion = args['opinion']

        try:
            # 1. 获取帖子
            post = SpeciesPost.query.get(post_id)
            if not post:
                return error(resid=404, msg=u'该鉴定贴不存在')

            # 2. 获取所选标签
            cand = SpeciesCandidate.query.get(cand_id)
            if not cand or cand.post_id != post_id:
                return error(resid=400, msg=u'所选物种标签不合法')

            # 3. 更新或覆盖鉴定结果
            # 不再判断 post.status == 1，允许专家修正之前的结论
            post.status = 1
            post.final_species_id = cand.id
            post.final_species_name = cand.species_name
            post.confirmed_by = g.user.id    # 记录最后一位鉴定的专家
            post.expert_opinion = opinion    # 覆盖旧的意见
            post.e_time = int(time.time())   # 更新鉴定时间

            db.session.commit()
            
            # 4. 刷新对象并返回简略信息
            db.session.refresh(post)

            return success(
                msg=u'专家鉴定已更新', 
                data=post, 
                data_fileds=get_expert_confirm_res_fields()
            )

        except Exception as e:
            db.session.rollback()
            # 这里的 print 有助于你在服务器后台看真实报错
            print(f"Expert Confirm Error: {str(e)}") 
            # 统一错误返回格式
            return error(resid=500, msg=u'服务器处理异常')