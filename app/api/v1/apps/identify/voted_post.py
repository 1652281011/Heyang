# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from flask import g
from flask_restful import Resource
from sqlalchemy.orm import joinedload
from app.api.common.response import success, error
from app.api.common.parser import species_voted_post_parser
from app.api.common.fields import get_ident_list_fields
from app.models.users import User
from app.models.identification import SpeciesPost, SpeciesVote
from app.models.base import db
from app.utils.decorators import login_required

class MyVotedSpeciesPostList(Resource):
    method_decorators = [login_required]

    def get(self):
        """
        获取当前用户参与过投票的帖子列表
        """
        user = g.user
        args = species_voted_post_parser()
        
        page = args['page']
        per_page = args['per_page']
        status = args.get('status')
        
        start_date_str = args.get('start_date')
        end_date_str = args.get('end_date')
        date_range = args.get('date_range')

        try:
            # 1. 核心查询：从 SpeciesPost 开始，关联 SpeciesVote
            # 筛选条件是 SpeciesVote.user_id 等于当前用户
            query = db.session.query(SpeciesPost).join(
                SpeciesVote, SpeciesVote.post_id == SpeciesPost.id
            ).filter(SpeciesVote.user_id == user.id)

            # 2. 状态过滤 (帖子状态)
            if status is not None:
                query = query.filter(SpeciesPost.status == status)

            # 3. 日期过滤 (基于投票时间 SpeciesVote.c_time)
            if start_date_str or end_date_str:
                if start_date_str:
                    st = datetime.strptime(start_date_str, '%Y-%m-%d')
                    query = query.filter(SpeciesVote.c_time >= int(st.timestamp()))
                if end_date_str:
                    et = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
                    query = query.filter(SpeciesVote.c_time < int(et.timestamp()))
            
            elif date_range and date_range != 'all':
                now_ts = int(time.time())
                if date_range == 'today':
                    start = datetime.combine(datetime.today(), datetime.min.time())
                    query = query.filter(SpeciesVote.c_time >= int(start.timestamp()))
                elif date_range == 'week':
                    query = query.filter(SpeciesVote.c_time >= now_ts - (7 * 24 * 3600))
                elif date_range == 'month':
                    query = query.filter(SpeciesVote.c_time >= now_ts - (30 * 24 * 3600))

            # 4. 预加载关联数据，避免 N+1
            query = query.options(
                joinedload(SpeciesPost.author),     # 发帖人信息
                joinedload(SpeciesPost.candidates)  # 候选标签
            ).order_by(SpeciesVote.c_time.desc())   # 按投票时间倒序

            # 5. 执行分页
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            # 6. 注入当前用户的投票 ID
            # 即使是列表，也要告诉前端我当时投了哪个，方便展示高亮
            for post in pagination.items:
                post.my_vote_id = post.get_user_vote_id(user.id)

            data = {
                'species_list': pagination.items,
                'pagination': {
                    'total': pagination.total,
                    'page': page,
                    'per_page': per_page,
                    'pages': pagination.pages
                }
            }

            return success(msg='获取投票历史成功', data=data, data_fileds=get_ident_list_fields())

        except ValueError:
            return error(msg="日期格式不正确")
        except Exception as e:
            return error(msg=f"查询失败: {str(e)}")