# -*- coding: utf-8 -*-
import requests
from flask import current_app
from flask_restful import Resource
from app.models.users import User
from app.api.common.response import success, error
from app.api.common.parser import wx_login_parser
from app.api.common.fields import user_fields # 复用之前的 fields

class WXLoginResource(Resource):
    def post(self):
        """
        微信小程序一键登录
        """
        args = wx_login_parser()
        code = args.get('code')

        params = {
            'appid': current_app.config['WX_APP_ID'],
            'secret': current_app.config['WX_APP_SECRET'],
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        
        try:
            res = requests.get(current_app.config['WX_LOGIN_URL'], params=params).json()
            openid = res.get('openid')
            # session_key = res.get('session_key') # 如果需要解密步数等敏感数据才用
            
            if not openid:
                return error(msg=u"微信验证失败: " + res.get('errmsg', 'Unknown Error'))
 
            # 2. 数据库匹配用户
            user = User.get_or_create_by_openid(openid)

            # 3. 更新用户信息 (可选：如果前端传了头像昵称)
            if args.get('nickname'): user.nickname = args.get('nickname')
            if args.get('avatar'): user.avatar = args.get('avatar')

            # 4. 生成 Token (注意 app_type 设为 'mp' 区分小程序和Web)
            token = user.generate_auth_token(app_type='mp')

            # 5. 组装数据并返回
            data = user.to_dict()
            data['auth_token'] = token

            return success(
                msg=u"登录成功",
                data=data,
                data_fileds=user_fields() # 复用之前的过滤规则
            )

        except Exception as e:
            current_app.logger.error(f"WX Login Error: {str(e)}")
            return error(msg=u"服务器通信异常")