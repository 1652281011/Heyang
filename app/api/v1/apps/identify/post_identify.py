# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import species_post_create_parser
from app.api.common.fields import op_id_fields
from app.models.identification import SpeciesPost, SpeciesCandidate
from app.models.users import User
from app.models.base import db
import time

class SpeciesPostAction(Resource):
    def post(self):
        # 1. 从 Header 获取 Auth-Token 并解析用户身份
        auth_token = request.headers.get('Auth-Token')
        if not auth_token:
            return error(resid=401, msg='请求头缺少 Auth-Token')
        
        user = User.verify_auth_token(auth_token)
        if not user:
            return error(resid=401, msg='登录已过期或 Token 无效')

        # 2. 解析其他参数 (此时 args 里不再有 user_id)
        args = species_post_create_parser()
        
        try:
            # 3. 创建帖子记录 (user_id 直接使用验证通过的 user.id)
            post = SpeciesPost(
                user_id=user.id,  # 核心改动：使用 Token 里的 id
                image_url=args['image_url'],
                description=args.get('description'),
                location_lat=args.get('lat'),
                location_lng=args.get('lng'),
                location_address=args.get('address'),
                participant_count=1,
                status=0,
                c_time=int(time.time()),
                e_time=int(time.time())
            )
            db.session.add(post)
            db.session.flush()

            # 4. 存入 AI 建议的标签
            for item in args['suggestions']:
                db.session.add(SpeciesCandidate(
                    post_id=post.id,
                    species_name=item['name'],
                    confidence=item['confidence'],
                    c_time=int(time.time()),
                    e_time=int(time.time())
                ))
            
            # 5. 更新用户的发帖总数
            user.post_count += 1
            
            db.session.commit()
            return success(msg='已成功发布到鉴定广场', data={'id': post.id}, data_fileds=op_id_fields())
            
        except Exception as e:
            db.session.rollback()
            # 生产环境建议移除具体的 str(e)，此处为了你方便调试保留
            return error(msg=f'发布失败: {str(e)}')