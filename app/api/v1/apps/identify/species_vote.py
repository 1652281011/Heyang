# -*- coding: utf-8 -*-
from os import error
from flask import g
from flask_restful import Resource
from app.api.common.fields import get_vote_res_fields
from app.api.common.parser import species_vote_parser
from app.api.common.response import success
from app.models.identification import SpeciesPost, SpeciesCandidate, SpeciesVote
from app.models.base import db
import time

from app.utils.decorators import login_required

class SpeciesVoteAction(Resource):
    method_decorators = [login_required]

    def post(self):
        user = g.user
        args = species_vote_parser()
        post_id = args['post_id']
        new_cand_id = args['candidate_id']

        try:
            # 1. 查找该用户在该贴的投票记录
            vote_rec = SpeciesVote.query.filter_by(user_id=user.id, post_id=post_id).first()
            post = SpeciesPost.query.get(post_id)
            if not post:
                return error(msg='帖子不存在')

            if vote_rec:
                # --- A. 修改投票逻辑 ---
                if vote_rec.candidate_id == new_cand_id:
                    # 如果投的是同一项，直接返回当前状态
                    post.my_vote_id = new_cand_id
                    return success(msg='已投过该项', data=post, data_fileds=get_vote_res_fields())

                # 减去旧标签票数
                old_cand = SpeciesCandidate.query.get(vote_rec.candidate_id)
                if old_cand:
                    old_cand.vote_count = max(0, old_cand.vote_count - 1)

                # 更新记录
                vote_rec.candidate_id = new_cand_id
                vote_rec.e_time = int(time.time())
                msg = '投票已修改'
            else:
                # --- B. 新增投票逻辑 ---
                db.session.add(SpeciesVote(
                    user_id=user.id,
                    post_id=post_id,
                    candidate_id=new_cand_id,
                    c_time=int(time.time()),
                    e_time=int(time.time())
                ))
                # 帖子总参与人数 +1
                post.participant_count += 1
                msg = '投票成功'

            # 无论新增还是修改，新标签票数都要 +1
            new_cand = SpeciesCandidate.query.get(new_cand_id)
            if new_cand:
                new_cand.vote_count += 1

            # 2. 提交到数据库
            db.session.commit()

            # 3. 关键：刷新 post 对象，确保 candidates 列表也是最新的
            db.session.refresh(post)
            # 动态注入 my_vote_id 供 fields 映射
            post.my_vote_id = new_cand_id

            return success(
                msg=msg, 
                data=post, 
                data_fileds=get_vote_res_fields()
            )

        except Exception as e:
            db.session.rollback()
            return error(msg=f"操作失败: {str(e)}")