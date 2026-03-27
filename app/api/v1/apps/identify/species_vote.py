# -*- coding: utf-8 -*-
import time
from flask import request
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import species_vote_parser
from app.api.common.fields import op_id_fields
from app.models.identification import SpeciesPost, SpeciesCandidate, SpeciesVote
from app.models.users import User
from app.models.base import db

class SpeciesVoteAction(Resource):
    def post(self):
        # 1. 安全校验：从 Header 获取 Auth-Token 并提取当前用户
        auth_token = request.headers.get('Auth-Token')
        if not auth_token:
            return error(resid=401, msg='未提供 Auth-Token，请登录')
        
        user = User.verify_auth_token(auth_token)
        if not user:
            return error(resid=401, msg='登录过期或 Token 无效')

        # 2. 参数解析
        args = species_vote_parser()
        post_id = args['post_id']
        candidate_id = args['candidate_id']

        # 3. 业务防重校验：检查该用户是否已经对该帖子投过票
        # 依靠数据库的 UNIQUE KEY (user_id, post_id) 也可以保证，但这里先进行业务拦截
        exists = SpeciesVote.query.filter_by(user_id=user.id, post_id=post_id).first()
        if exists:
            return error(msg='您已参与过该鉴定，请勿重复投票')

        try:
            # 4. 执行原子性操作 (事务)
            
            # A. 插入投票详情记录
            new_vote = SpeciesVote(
                user_id=user.id,        # 关键：使用 Token 中的 user.id
                post_id=post_id,
                candidate_id=candidate_id,
                c_time=int(time.time()),
                e_time=int(time.time())
            )
            db.session.add(new_vote)

            # B. 对应候选词条的 vote_count 自增
            candidate = SpeciesCandidate.query.get(candidate_id)
            if not candidate or candidate.post_id != post_id:
                return error(msg='候选词条不存在或不属于该帖子')
            candidate.vote_count += 1

            # C. 主贴的参与人数 participant_count 自增
            post = SpeciesPost.query.get(post_id)
            if post:
                post.participant_count += 1
            
            # 5. 提交数据库
            db.session.commit()
            
            return success(
                msg='投票成功', 
                data={'id': new_vote.id}, 
                data_fileds=op_id_fields()
            )

        except Exception as e:
            db.session.rollback()
            return error(msg=f'投票系统繁忙: {str(e)}')