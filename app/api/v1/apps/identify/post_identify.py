# -*- coding: utf-8 -*-
from flask import g
from flask_restful import Resource
from app.api.common.response import success, error

from app.api.common.parser import species_post_create_parser
from app.api.common.fields import get_post_create_res_fields, op_id_fields
from app.models.identification import SpeciesPost, SpeciesCandidate
from app.models.base import db
import time

from app.utils.decorators import login_required

class SpeciesPostAction(Resource):
    method_decorators = [login_required]

    def post(self):
        user = g.user
        args = species_post_create_parser()
        
        try:
            post = SpeciesPost(
                user_id=user.id,
                image_url=args['image_url'],
                description=args.get('description', ''),
                location_lat=args.get('lat'),
                location_lng=args.get('lng'),
                location_address=args.get('address', ''),
                status=0,            # 初始：待鉴定
                participant_count=1,  # 初始：发帖人1人
                c_time=int(time.time()),
                e_time=int(time.time())
            )
            db.session.add(post)
            # flush 以便获取 post.id 供候选标签使用
            db.session.flush()

            # 3. 循环插入候选标签
            for item in args['suggestions']:
                candidate = SpeciesCandidate(
                    post_id=post.id,
                    species_name=item['name'],
                    confidence=item.get('confidence', 0),
                    vote_count=0,
                    c_time=int(time.time()),
                    e_time=int(time.time())
                )
                db.session.add(candidate)
            
            # 4. 更新用户发帖统计
            user.post_count += 1
            
            # 5. 提交事务
            db.session.commit()
            
            # 6. 关键：重新刷新 post 对象，确保关联的 candidates 能被加载
            db.session.refresh(post)

            # 7. 返回结果：data 直接传入 post 对象，data_fileds 传入新的定义
            return success(
                msg='帖子发布成功', 
                data=post, 
                data_fileds=get_post_create_res_fields()
            )

        except Exception as e:
            db.session.rollback()
            return error(msg=f"发布失败: {str(e)}")