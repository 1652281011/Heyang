# -*- coding: utf-8 -*-
import random
import time
from threading import Thread
from flask import current_app
from flask_mail import Message
from app import db, mail, redis_store
from app.api.common import error_code
from app.models.users import User
from email.utils import make_msgid 
import traceback

from app.utils.uploader import Uploader

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"[Email Error] Failed: {repr(e)}")

class UserService:
    @staticmethod
    def send_code(email, code_type):
        user_exists = User.query.filter_by(email=email).first()
        if code_type == '1': # 注册检查
            if user_exists: return False, error_code.USER_IS_EXISTS, u"该邮箱已被注册"
            redis_prefix, subject = "reg", "Registration Code"
        elif code_type == '2':
            if not user_exists: return False, error_code.USER_NOT_EXISTS, u"该邮箱未注册"
            redis_prefix, subject = "reset", "Reset Password Code"
        else: # code_type == '3' 修改邮箱
            # 修改后的新邮箱不能是系统中已有的邮箱
            if user_exists: return False, error_code.USER_IS_EXISTS, u"新邮箱已被占用"
            redis_prefix, subject = "modify", "Modify Email Code"

        code = str(random.randint(100000, 999999))
        try:
            redis_store.set(f"{redis_prefix}:{email}", code, ex=300)
        except:
            return False, error_code.API_TEMPORARY_NOT_USABLE, u"服务器缓存异常"

        msg = Message(subject=subject, recipients=[email.strip()], sender=current_app.config.get('MAIL_USERNAME'))
        msg.body = f"Your code is: {code}. Valid for 5 minutes."
        msg.msgId = make_msgid(domain='localhost') # 修复中文计算机名报错

        app = current_app._get_current_object()
        Thread(target=send_async_email, args=(app, msg)).start()
        return True, None, u"验证码已发送"

    @staticmethod
    def register(args):
        saved_code = redis_store.get(f"reg:{args['email']}")
        if isinstance(saved_code, bytes): saved_code = saved_code.decode('utf-8')
        if not saved_code or str(saved_code) != str(args['code']):
            return None, error_code.PARAMS_NOT_LEGAL, u"验证码错误或已过期"
        
        user, msg = User.create_user(args['username'], args.get('nickname','momo'), args['password'], "1", args['email'])
        if user: redis_store.delete(f"reg:{args['email']}")
        return user, None, msg

    @staticmethod
    def reset_password(email, code, new_password):
        saved_code = redis_store.get(f"reset:{email}")
        if isinstance(saved_code, bytes): saved_code = saved_code.decode('utf-8')
        if not saved_code or str(saved_code) != str(code):
            return False, error_code.PARAMS_NOT_LEGAL, u"验证码错误或已过期"

        user = User.query.filter_by(email=email).first()
        try:
            from werkzeug.security import generate_password_hash
            user.password = generate_password_hash(new_password)
            db.session.commit()
            redis_store.delete(f"reset:{email}")
            return True, None, u"密码重置成功"
        except:
            db.session.rollback()
            return False, error_code.DATABASE_TABLE_UPDATE_ERROR, u"更新失败"

    @staticmethod
    def login(account, password):
        user = User.query.filter((User.username == account) | (User.email == account)).first()
        if not user or not user.check_password(password):
            return None, error_code.USER_PASSWORD_NOT_CORRECT, u"账号或密码错误"
        
        token = user.generate_auth_token()
        res = user.to_dict()
        res['auth_token'] = token
        return res, None, u"登录成功"
    
    @staticmethod
    def update_profile(user_id, args):
        """
        更新用户信息 Service 完整版
        :param user_id: 当前登录用户的 ID
        :param args: 解析后的参数字典
        :return: (data, code, msg)
        """
        # 1. 获取用户对象
        user = User.query.get(user_id)
        if not user:
            return None, error_code.USER_NOT_EXISTS, u"用户不存在"

        # 2. 处理邮箱修改 (核心优化：需要验证码)
        new_email = args.get('email')
        if new_email and new_email != user.email:
            code = args.get('code')
            if not code:
                return None, error_code.PARAMS_NOT_LEGAL, u"修改邮箱需要提供验证码"
            
            # 校验 Redis 中的修改邮箱验证码 (前缀为 modify)
            saved_code = redis_store.get(f"modify:{new_email}")
            if isinstance(saved_code, bytes):
                saved_code = saved_code.decode('utf-8')
            
            if not saved_code or str(saved_code) != str(code):
                return None, error_code.PARAMS_NOT_LEGAL, u"验证码错误或已过期"
            
            # 检查新邮箱是否被其他用户占用
            is_exist = User.query.filter(User.email == new_email, User.id != user_id).first()
            if is_exist:
                return None, error_code.USER_IS_EXISTS, u"该新邮箱已被其他账号占用"
            
            # 校验通过，执行修改并清理缓存
            user.email = new_email
            redis_store.delete(f"modify:{new_email}")

        # 3. 处理标签操作 (add / delete)
        tag_action = args.get('tag_action')
        tag_name = args.get('tag_name')
        if tag_action and tag_name:
            if tag_action == "add":
                user.add_tag(tag_name)
            elif tag_action == "delete":
                user.delete_tag(tag_name)

        # 4. 处理基本资料 (nickname, bio)
        if args.get('nickname'):
            user.nickname = args['nickname']
        
        # bio 允许传空字符串，所以用 is not None 判断
        if args.get('bio') is not None:
            user.bio = args['bio']

        # 5. 处理头像上传 (使用 Uploader 工具类)
        avatar_file = args.get('avatar')
        if avatar_file:
            # 构造 Uploader 配置
            upload_config = {
                "pathFormat": "uploads/avatar/{yyyy}{mm}{dd}/{time}{rand:6}",
                "maxSize": 2 * 1024 * 1024, # 限制 2MB
                "allowFiles": [".png", ".jpg", ".jpeg", ".gif"],
                "oriName": avatar_file.filename
            }
            # 这里的 current_app.static_folder 确保文件上传到静态资源目录
            uploader = Uploader(avatar_file, upload_config, current_app.static_folder)
            
            if uploader.stateInfo == "SUCCESS":
                # 保存上传成功后的相对路径
                user.avatar = uploader.getFileInfo()['url']
            else:
                # 如果上传失败（如格式不对、文件过大），直接拦截并返回
                return None, error_code.FILE_UPLOAD_ERROR, uploader.stateInfo

        # 6. 更新活跃/修改时间
        user.e_time = int(time.time())

        # 7. 提交数据库事务
        try:
            db.session.add(user)
            db.session.commit()
            # 刷新对象以确保获取到数据库最新状态
            db.session.refresh(user)
            return user.to_dict(), None, u"个人资料更新成功"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Update Profile DB Error [UID:{user_id}]: {str(e)}")
            return None, error_code.DATABASE_TABLE_UPDATE_ERROR, u"数据库更新失败"