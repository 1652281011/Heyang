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
  

def professional_apply_parser():
    """用户提交申请的参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('real_name', type=str, required=True, location='form', help='姓名')
    parser.add_argument('pro_title', type=str, location='form', help='职称')
    parser.add_argument('organization', type=str, location='form', help='机构')
    parser.add_argument('expertise_field', type=str, location='form', help='研究领域')
    # 证明材料图片
    parser.add_argument('certificate', type=werkzeug.datastructures.FileStorage, location='files', required=True,  help="请上传证明材料(图片或PDF/Doc)")
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

def professional_list_parser():
    """管理后台查询申请列表的参数解析器"""
    parser = reqparse.RequestParser()
    # GET 请求参数使用 location='args'
    parser.add_argument('status', type=int, location='args', help="状态筛选: 0待审, 1通过, 2驳回")
    parser.add_argument('search', type=str, location='args', help="搜索关键词: 昵称/账号/姓名/手机")
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args')
    return parser.parse_args()

def professional_audit_parser():
    """管理员审批参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=int, required=True, location='json', help='待审核者id')
    parser.add_argument('action', type=int, required=True, choices=[1, 2], help="1:通过, 2:驳回", location='json')
    parser.add_argument('reason', type=str, location='json', help='驳回理由')
    return parser.parse_args()

def admin_pro_detail_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=int, required=True, location='args', help="必须提供用户ID")
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
    """发布帖子参数解析器"""
    parser = reqparse.RequestParser()

    parser.add_argument('title', type=str, location='form', required=True, help="标题不能为空")
    parser.add_argument('content', type=str, location='form', required=True, help="内容不能为空")

    parser.add_argument('is_public', type=int, location='form', default=1)
    parser.add_argument('images', type=werkzeug.datastructures.FileStorage, location='files', action='append', required=False, help="帖子图片")
    
    return parser.parse_args()

def post_delete_parser():
    parser = reqparse.RequestParser()
    # 删帖通常通过 URL 参数或 JSON 传参
    parser.add_argument('post_id', type=int, required=True, location=['json', 'args'], help="帖子ID不能为空")
    return parser.parse_args()

def post_update_parser(): 
    """修改帖子参数解析器 (仅限文本和状态)"""
    parser = reqparse.RequestParser()
    # 帖子ID必须传
    parser.add_argument('post_id', type=int, required=True, location='json', help="帖子ID不能为空")
    
    # 以下为可选修改字段
    parser.add_argument('title', type=str, location='json')
    parser.add_argument('content', type=str, location='json')
    parser.add_argument('is_public', type=int, location='json') # 1:公开, 0:私密
    
    return parser.parse_args()

def post_interact_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('post_id', type=int, location='json', required=True)
    parser.add_argument('content', type=str, location='json') # 仅评论需要
    return parser.parse_args()


# 用户通用参数

def user_register_parser():
    parser = reqparse.RequestParser()

    parser.add_argument('username', type=is_mobile, location='json', required=True, help=u'手机号')
    parser.add_argument('password', type=str, location='json', required=True, help=u'密码')

    return parser.parse_args()

def user_sign_in_parser():
    parser = reqparse.RequestParser()

    parser.add_argument('username', type=is_mobile, location='json', required=True, help=u'手机号')
    parser.add_argument('password', type=str, location='json', required=True, help=u'密码')
    
    return parser.parse_args()

def user_update_parser():
    """修改基本信息参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('nickname', type=str, location='form', required=False, help=u'新昵称')
    parser.add_argument('avatar', type=werkzeug.datastructures.FileStorage, 
                        location='files', required=False)
    parser.add_argument('bio', type=str, location='form', required=False, help=u'简介')
    parser.add_argument('email', type=str, location='form', required=False, help=u'邮箱')

    parser.add_argument('tag_action', type=str, location='form', required=False, help=u'标签操作')
    parser.add_argument('tag_name', type=str, location='form', required=False, help=u'标签内容')
    return parser.parse_args()

def user_password_update_parser():
    """修改密码参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('old_password', type=str, location='json', required=True, help=u'旧密码必填')
    parser.add_argument('new_password', type=str, location='json', required=True, help=u'新密码必填')
    return parser.parse_args()

# --- 1. AI识别预览阶段 ---
def species_ident_preview_parser():
    """上传图片进行AI识别预览时的参数"""
    parser = reqparse.RequestParser()
    # 接收文件对象，location='files' 对应 multipart/form-data
    parser.add_argument(
        'image', 
        type=werkzeug.datastructures.FileStorage, 
        location='files', 
        required=True, 
        help=u'请上传待识别的物种图片'
    )
    return parser.parse_args()

# --- 2. 广场列表筛选阶段 ---
def species_post_search_parser():
    """获取鉴定广场列表时的分页与过滤参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args')
    parser.add_argument(
        'status', 
        type=int, 
        choices=[0, 1], 
        location='args', 
        help=u'状态过滤：0待鉴定, 1已确认'
    )
    return parser.parse_args()

# --- 3. 发起鉴定贴阶段 ---
def species_post_create_parser():
    """用户正式发布鉴定请求到广场的参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('image_url', type=str, required=True, location='json', help=u'图片地址不能为空')
    parser.add_argument('description', type=str, location='json')
    
    # 地理位置信息 (float类型接收经纬度)
    parser.add_argument('lat', type=float, location='json', help=u'纬度坐标')
    parser.add_argument('lng', type=float, location='json', help=u'经度坐标')
    parser.add_argument('address', type=str, location='json', help=u'地理位置描述')
    
    # AI给出的建议标签列表，接收JSON Array: [{"name": "xxx", "confidence": 0.9}, ...]
    parser.add_argument(
        'suggestions', 
        type=list, 
        location='json', 
        required=True, 
        help=u'算法识别结果列表不能为空'
    )
    return parser.parse_args()

# --- 4. 社区投票阶段 ---
def species_vote_parser():
    """用户对某个候选物种标签进行投票"""
    parser = reqparse.RequestParser()
    parser.add_argument('post_id', type=int, required=True, location='json', help=u'帖子ID不能为空')
    parser.add_argument('candidate_id', type=int, required=True, location='json', help=u'所选标签ID不能为空')
    return parser.parse_args()

# --- 5. 专家确认阶段 ---
def species_expert_confirm_parser():
    """专家或管理员最终确认物种结果"""
    parser = reqparse.RequestParser()
    parser.add_argument('post_id', type=int, required=True, location='json', help=u'帖子ID不能为空')
    parser.add_argument('candidate_id', type=int, required=True, location='json', help=u'确定的正确候选标签ID不能为空')
    return parser.parse_args()

def wx_login_parser():
    parser = reqparse.RequestParser()
    # 小程序通过 wx.login() 获取的 code
    parser.add_argument('code', type=str, required=True, location='json', help="code不能为空")
    # 可选：头像和昵称（如果前端已获取）
    parser.add_argument('nickname', type=str, location='json')
    parser.add_argument('avatar', type=str, location='json')
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