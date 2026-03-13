# -*- coding: utf-8 -*-
import re
from flask_restful import reqparse
import werkzeug

# 工具函数
def is_mobile(mobile_str):
    """验证手机号格式"""
    if not re.match(r'^1[3-9]\d{9}$', str(mobile_str).strip()):
        raise ValueError(f"{mobile_str} is not a valid mobile")
    return str(mobile_str).strip()

def is_email(email_str):
    """验证邮箱格式"""
    email_str = str(email_str).strip()
    # 简单的邮箱正则
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email_str):
        raise ValueError(f"{email_str} 不是有效的邮箱格式")
    return email_str

def parse_bool(value):
    """自定义布尔类型解析函数"""
    if isinstance(value, str):
        return value.lower() == 'true' or value == '1'
    elif isinstance(value, int):
        return value == 1
    return bool(value)
  

# 教授 (Professor) 相关解析器
def professor_sign_up_parser():
    """教授注册参数解析"""
    parser = reqparse.RequestParser()
    parser.add_argument('email', type=is_email, required=True, location='json', help='请输入有效的邮箱地址')   
    parser.add_argument('password', type=str, required=True, location='json', help='密码不能为空')
    parser.add_argument('professor_name', type=str, required=True, location='json', help='姓名不能为空')
    
    # 选填项
    parser.add_argument('gender', type=str, location='json', choices=['男', '女'])
    parser.add_argument('title', type=str, location='json')
    parser.add_argument('organization', type=str, location='json')
    
    return parser.parse_args()

def professor_sign_in_parser():
    """教授登录参数解析"""
    parser = reqparse.RequestParser()
    parser.add_argument('email', type=is_email, required=True, location='json', help='请输入登录邮箱')   
    parser.add_argument('password', type=str, required=True, location='json', help='密码不能为空')
    return parser.parse_args()


# 物种 (Species) 相关解析器
def species_search_parser():
    """物种列表搜索"""
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args', help='页码')
    parser.add_argument('per_page', type=int, default=20, location='args', help='每页数量')
    parser.add_argument('keyword', type=str, location='args', help='通用搜索关键词')
    parser.add_argument('species', type=str, location='args', help='种')
    parser.add_argument('order_name', type=str, location='args', help='目')
    parser.add_argument('family', type=str, location='args', help='科')
    return parser.parse_args()

def species_detail_parser():
    """物种详情"""
    parser = reqparse.RequestParser()
    parser.add_argument('species_id', type=str, required=True, location='args')
    return parser.parse_args()

def species_upload_parser():
    """物种上传/修改"""
    parser = reqparse.RequestParser()
    # 核心控制字段
    parser.add_argument('operate_type', type=str, required=True, choices=['add', 'update'], help='操作类型必须为 add 或 update', location='json')
    parser.add_argument('scientific_name', type=str, required=True, location='json', help='物种学名不能为空')
    
    # 业务数据字段
    parser.add_argument('chinese_name', type=str, required=True, location='json')
    parser.add_argument('english_name', type=str, location='json')
    parser.add_argument('species', type=str, required=True, location='json')
    parser.add_argument('order_name', type=str, required=True, location='json')
    parser.add_argument('family', type=str, required=True, location='json')
    parser.add_argument('description', type=str, location='json')
    # 可根据需要补充 collection_province, grade 等字段
    
    return parser.parse_args()


# 管理员 (Admin) 相关解析器
def admin_sign_in_parser():
    """管理员登录"""
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, location='json', required=True, help=u'用户名')
    parser.add_argument('password', type=str, location='json', required=True, help=u'密码')
    return parser.parse_args()

def admin_register_parser():
    """管理员注册"""
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, location='json', required=True, help=u'用户名')
    parser.add_argument('password', type=str, location='json', required=True, help=u'密码')
    parser.add_argument('email', type=str, location='json', required=True, help=u'邮箱')
    parser.add_argument('mobile', type=str, location='json', required=True, help=u'手机号')
    parser.add_argument('real_name', type=str, location='json', required=True, help=u'真实姓名')
    return parser.parse_args()

def admin_search_parser():
    """管理员列表搜索"""
    parser = reqparse.RequestParser()
    parser.add_argument('keyword', type=str, location='args', required=False, help=u'关键词')
    parser.add_argument('status', type=str, location='args', required=False, help=u'状态')
    parser.add_argument('page', type=int, location='args', required=False, default=1, help=u'页码')
    parser.add_argument('per_page', type=int, location='args', required=False, default=20, help=u'每页数量')
    return parser.parse_args()

def admin_status_update_parser():
    """管理员状态修改"""
    parser = reqparse.RequestParser()
    parser.add_argument('admin_id', type=int, location='json', required=True, help=u'管理员id')
    parser.add_argument('status', type=str, location='json', required=True, trim=True, help=u'状态值')
    return parser.parse_args()

def audit_list_parser():
    """审核列表查询"""
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args', help='页码')
    parser.add_argument('per_page', type=int, default=20, location='args', help='每页数量')
    parser.add_argument('status', type=str, default='0', location='args', help='审核状态')
    return parser.parse_args()

def audit_action_parser():
    """审核操作"""
    parser = reqparse.RequestParser()
    parser.add_argument('audit_id', type=int, required=True, location='json')
    parser.add_argument('action', type=str, required=True, choices=['pass', 'reject'], location='json')
    parser.add_argument('reject_reason', type=str, location='json')
    return parser.parse_args()

"""社区相关"""

def post_list_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('keyword', type=str, location='args', help=u'关键词')
    parser.add_argument('page', type=int, location='args', default=1)
    parser.add_argument('per_page', type=int, location='args', default=10)
    return parser.parse_args()

def post_detail_parser():
    """详情页参数解析"""
    parser = reqparse.RequestParser()
    parser.add_argument('post_id', type=int, location='args', required=True, help=u'帖子ID必传')
    return parser.parse_args()

def post_publish_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('title', type=str, location='form', required=True, help=u'标题必填')
    parser.add_argument('content', type=str, location='form', required=True, help=u'内容必填')
    parser.add_argument('user_id', type=int, location='form', required=True)
    parser.add_argument('images', type=werkzeug.datastructures.FileStorage, location='files', action='append')
    return parser.parse_args()

def post_interact_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('post_id', type=int, location='json', required=True)
    parser.add_argument('user_id', type=int, location='json', required=True)
    parser.add_argument('content', type=str, location='json') # 仅评论需要
    return parser.parse_args()


# 兼容性/通用 解析器 (防止旧的 import 报错)
def sign_up_parser():
    """普通用户注册(保留以防报错)"""
    parser = reqparse.RequestParser()
    parser.add_argument('mobile', type=is_mobile, location='json', required=True, help=u'手机号')
    parser.add_argument('name', type=str, location='json', required=False)
    parser.add_argument('password', type=str, location='json', required=False)
    return parser.parse_args()

def sign_in_wapplet_parser():
    """小程序登录(保留以防报错)"""
    parser = reqparse.RequestParser()
    parser.add_argument('code', type=str, location='json', required=True)
    parser.add_argument('encryptedData', type=str, location='json')
    parser.add_argument('iv', type=str, location='json')
    parser.add_argument('nickName', type=str, location='json')
    return parser.parse_args()

def login_parser():
    """通用登录(保留以防报错)"""
    parser = reqparse.RequestParser()
    parser.add_argument('mobile', type=str, required=True, location='json')
    parser.add_argument('password', type=str, required=True, location='json')
    return parser.parse_args()

def userBeginOnPage_parser():
    """埋点相关(保留以防报错)"""
    parser = reqparse.RequestParser()
    parser.add_argument('beginTime', type=str, location='json')
    return parser.parse_args()

def user_parser(method='post'):
    """通用用户查询(保留以防报错)"""
    parser = reqparse.RequestParser()
    if method == 'get':
        parser.add_argument('participant_id', type=str, location='args')
    return parser.parse_args()

def test_parser():
    """
    测试用参数解析器 (兼容旧代码)
    """
    # 确保文件顶部导入了 reqparse
    # from flask_restful import reqparse 
    
    parser = reqparse.RequestParser()
    parser.add_argument('foo', type=int, location=['json', 'args'], required=False, help=u'The foo')
    parser.add_argument('pw', type=str, location=['json', 'args'], required=False, help=u'The pw')
    return parser.parse_args()