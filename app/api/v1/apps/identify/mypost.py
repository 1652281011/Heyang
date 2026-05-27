# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
import time
from flask import g
from flask_restful import Resource
from sqlalchemy.orm import joinedload
from app.api.common.response import success, error
from app.api.common.parser import species_my_post_parser
from app.api.common.fields import get_ident_list_fields
from app.models.identification import SpeciesPost
from app.models.users import User
from app.utils.decorators import login_required

class MySpeciesPostList(Resource):
    method_decorators = [login_required]

    def get(self):
        user = g.user
        args = species_my_post_parser()
        
        page = args['page']
        per_page = args['per_page']
        status = args.get('status')
        
        # 筛选参数
        date_range = args.get('date_range')
        start_date_str = args.get('start_date')
        end_date_str = args.get('end_date')

        try:
            # 1. 基础查询
            query = SpeciesPost.query.filter_by(user_id=user.id)

            # 2. 状态过滤
            if status is not None:
                query = query.filter_by(status=status)

            # 3. 自定义日期范围逻辑 (优先级最高)
            if start_date_str or end_date_str:
                if start_date_str:
                    # 转换开始日期为当天 00:00:00
                    start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
                    start_ts = int(start_dt.timestamp())
                    query = query.filter(SpeciesPost.c_time >= start_ts)
                
                if end_date_str:
                    # 转换结束日期为当天 23:59:59
                    end_dt = datetime.strptime(end_date_str, '%Y-%m-%d')
                    # 加一天减一秒，或者直接设为 23:59:59
                    end_ts = int((end_dt + datetime.timedelta(days=1)).timestamp()) - 1
                    query = query.filter(SpeciesPost.c_time <= end_ts)
            
            # 4. 快捷日期筛选逻辑 (如果没有传自定义日期)
            elif date_range and date_range != 'all':
                now_ts = int(time.time())
                if date_range == 'today':
                    today_start = datetime.combine(datetime.date.today(), datetime.min.time())
                    query = query.filter(SpeciesPost.c_time >= int(today_start.timestamp()))
                elif date_range == 'week':
                    query = query.filter(SpeciesPost.c_time >= now_ts - (7 * 24 * 3600))
                elif date_range == 'month':
                    query = query.filter(SpeciesPost.c_time >= now_ts - (30 * 24 * 3600))

            # 5. 排序与分页
            pagination = query.options(
                joinedload(SpeciesPost.candidates)
            ).order_by(SpeciesPost.c_time.desc()).paginate(page=page, per_page=per_page)

            # 6. 注入投票状态
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

            return success(msg='获取个人作品成功', data=data, data_fileds=get_ident_list_fields())

        except ValueError:
            return error(msg="日期格式错误，请使用 YYYY-MM-DD 格式")
        except Exception as e:
            return error(msg=f"查询异常: {str(e)}")