#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/29 上午12:01
# @Software：PyCharm
# @Author  : scott
from flask_restful import fields
from sqlalchemy import Float


def common_fields(data_fileds=None, is_list=False):
    """
        公共数据
        :param resid: 错误码
        :param msg: 错误消息
        :param status: 处理结果状态
        :param data: 返回数据
        :param data_fileds: 返回数据字段
        :return:
    """
    _common_fields = {
        "resid": fields.Integer(default=200),
        "msg": fields.String(default=u'请求成功'),
        "status": fields.String(default=u'success')
    }
    if data_fileds:
        if not is_list:
            _common_fields.update(data=fields.Nested(data_fileds))
        else:
            _common_fields.update(data=fields.List(fields.Nested(data_fileds)))
    return _common_fields

def test_fields():
    data_fields = {
        'data': fields.String
    }
    return common_fields(data_fields)

# app/api/common/fields.py
from flask_restful import fields

def user_full_info_fields():
    # 专业身份补充信息结构
    pro_data_fields = {
        'real_name': fields.String,
        'pro_title': fields.String,
        'organization': fields.String,
        'expertise_field': fields.String,
        'certificate_file': fields.String,
    }

    data_fields = {
        'id': fields.Integer,
        'username': fields.String,     # 手机号
        'nickname': fields.String,
        'avatar': fields.String,
        'email': fields.String,
        'bio': fields.String,
        'tags': fields.String,
        'role_type': fields.String,    # '1'普通, '2'专业
        'post_count': fields.Integer,  # 总动态数
        'total_likes': fields.Integer(attribute='total_like_count'), # 获赞总数
        'register_time': fields.String(attribute='c_time_format'),
        'last_login_time': fields.String(attribute='e_time_format'),
        # 如果是专业用户，返回此对象，否则为 null
        'professional_details': fields.Nested(pro_data_fields, attribute='active_pro_details', allow_null=True)
    }
    
    return common_fields(data_fields)


def user_fields():
    data_fields = {
        'username': fields.String(default=''),   # 手机号
        'nickname': fields.String(default=''),   # 昵称
        'e_time': fields.String(default=''),      # 登陆时间
        'role_type': fields.String(default=''),
        'auth_token': fields.String(default='')  # 登录凭证
    }
    return common_fields(data_fields)

def user_upd_fields():
    data_fields = {
        'username': fields.String(default=''),    # 手机号
        'nickname': fields.String(default=''),    # 昵称
        'avatar': fields.String(default=''),      # 头像地址
        'email': fields.String(default=''),       # 邮箱
        'bio': fields.String(default=''),         # 简介
        'tags': fields.String(default=''),        # 标签串
        'e_time': fields.String(attribute='e_time', default=''), # 修改/登录时间
    }
    return common_fields(data_fields)

def post_fields():
    data_fields = {
        'post_id': fields.Integer(attribute='id', default=0), # 帖子ID (映射模型里的id)
        'title': fields.String(default=''),                    # 标题
        'content': fields.String(default=''),                  # 内容
        'images': fields.List(fields.String, default=[]),      # 图片URL列表
        'author': fields.String(attribute='author_nickname', default=''), # 作者昵称
        'c_time': fields.String(attribute='create_time', default=''),     # 创建时间
        'is_public': fields.Integer(default=1),
        'view_count': fields.Integer(default=0),               # 阅读数
        'like_count': fields.Integer(default=0),               # 点赞数
        'comment_count': fields.Integer(default=0)             # 评论数
    }
    return common_fields(data_fields)

def professional_admin_list_fields():
    """专业申请列表的字段定义"""
    item_fields = {
        'user_id': fields.Integer,
        'username': fields.String(attribute='user.username'), # 跨表取数据
        'nickname': fields.String(attribute='user.nickname'),
        'real_name': fields.String,
        'mobile': fields.String,
        'pro_title': fields.String,
        'organization': fields.String,
        'audit_status': fields.Integer,
        'apply_time': fields.String(attribute='apply_time_format'), # 使用模型里的 property
        'audit_time': fields.String(attribute='audit_time_format')
    }
    
    data_fields = {
        'list': fields.List(fields.Nested(item_fields)),
        'total': fields.Integer,
        'page': fields.Integer,
        'per_page': fields.Integer
    }
    return common_fields(data_fields)

def professional_audit_result_fields():
    data_fields = {
        'user_id': fields.Integer,
        'username': fields.String(attribute='user.username'),
        'nickname': fields.String(attribute='user.nickname'),
        'avatar': fields.String(attribute='user.avatar'),
        
        'real_name': fields.String,
        'pro_title': fields.String,
        'organization': fields.String,
        'certificate_file': fields.String,
        'expertise_field': fields.String,
        
        'audit_status': fields.Integer,
        'reject_reason': fields.String,
        'auditor': fields.String(attribute='auditor_name'),
        'apply_time': fields.String(attribute='apply_time_format'),
        'audit_time': fields.String(attribute='audit_time_format')
    }
    return common_fields(data_fields)



def post_list_fields():
    # 单个帖子的格式定义
    item_fields = {
        'id': fields.Integer,
        'title': fields.String,
        'author': fields.String(attribute='author_nickname'),
        'cover': fields.String(attribute='cover_url'),
        'like_count': fields.Integer,
        'comment_count': fields.Integer,
        'view_count': fields.Integer,    # <--- 【新增】添加浏览量字段
        'create_time': fields.String(attribute='c_time_str')
    }

    data_dict_fields = {
        'list': fields.List(fields.Nested(item_fields)),
        'total': fields.Integer,
        'page': fields.Integer
    }

    return common_fields(data_dict_fields)

def post_detail_fields():
    # 1. 评论项格式
    comment_item = {
        'id': fields.Integer,
        'content': fields.String,
        'nickname': fields.String(attribute='user.nickname'), # 关联获取评论者昵称
        'avatar': fields.String(attribute='user.avatar_url'),       
        'create_time': fields.String(attribute='c_time_str')
    }

    # 2. 详情主体格式
    data_dict_fields = {
        'id': fields.Integer,
        'title': fields.String,
        'content': fields.String,
        'view_count': fields.Integer,
        'like_count': fields.Integer,
        'comment_count': fields.Integer,
        'is_liked': fields.Boolean,          # 当前用户是否已点赞
        'images': fields.List(fields.String(attribute='url')), # 图片URL列表
        'author': {
            'nickname': fields.String(attribute='author.nickname'),
            'avatar': fields.String(attribute='author.avatar_url'),
        },
        'comments': fields.List(fields.Nested(comment_item)), # 评论列表嵌套
        'create_time': fields.String(attribute='c_time_str')
    }

    # 使用 common_fields 包装成统一的 {resid, msg, status, data}
    return common_fields(data_dict_fields)

def ai_preview_fields():
    """AI识别预览结果"""
    data_fields = {
        'image_url': fields.String,
        'suggestions': fields.List(fields.Nested({
            'name': fields.String,
            'confidence': fields.Float
        }))
    }
    return common_fields(data_fields)

def get_ident_list_fields():
    """鉴定广场列表展示字段"""
    post_item = {
        'id': fields.Integer,
        'nickname': fields.String(attribute='author.nickname'),
        'image_url': fields.String(attribute='full_image_url'),
        'description': fields.String,
        'status': fields.Integer,
        'final_species_name': fields.String,
        # 地理位置、参与人数、时间
        'lat': fields.Float(attribute='location_lat'),
        'lng': fields.Float(attribute='location_lng'),
        'address': fields.String(attribute='location_address'),
        'participant_count': fields.Integer,
        'upload_time': fields.String(attribute='upload_time_str'), # 对应模型中的格式化方法
        'my_vote_id': fields.Integer(default=0),
        'candidates': fields.List(fields.Nested({
            'id': fields.Integer,
            'species_name': fields.String,
            'confidence': fields.Float,
            'vote_count': fields.Integer
        }))
    }
    data_fields = {
        'species_list': fields.List(fields.Nested(post_item)),
        'pagination': fields.Nested({
            'total': fields.Integer, 'page': fields.Integer, 
            'per_page': fields.Integer, 'pages': fields.Integer
        })
    }
    return common_fields(data_fields)

def get_post_create_res_fields():
    """
    发布帖子后的返回字段定义
    包含：基本信息、状态、参与人数、格式化时间、候选标签列表
    """
    candidate_item = {
        'id': fields.Integer,
        'species_name': fields.String,
        'confidence': fields.Float,
        'vote_count': fields.Integer
    }

    data_fields = {
        'id': fields.Integer,
        'image_url': fields.String(attribute='full_image_url'),
        'description': fields.String,
        'status': fields.Integer,
        'participant_count': fields.Integer,
        'upload_time': fields.String(attribute='format_time'), # 对应模型中的 format_time 属性
        'lat': fields.Float(attribute='location_lat'),
        'lng': fields.Float(attribute='location_lng'),
        'address': fields.String(attribute='location_address'),
        'candidates': fields.List(fields.Nested(candidate_item))
    }

    return common_fields(data_fields)

def get_vote_res_fields():
    """
    投票操作成功后的返回字段
    用于实时刷新前端的票数进度条和参与人数
    """
    # 候选标签项（含更新后的票数）
    candidate_item = {
        'id': fields.Integer,
        'species_name': fields.String,
        'vote_count': fields.Integer
    }

    data_fields = {
        'post_id': fields.Integer(attribute='id'),
        'participant_count': fields.Integer,
        'my_vote_id': fields.Integer, # 当前用户最终投给的标签ID
        'candidates': fields.List(fields.Nested(candidate_item))
    }

    return common_fields(data_fields)

def get_expert_confirm_res_fields():
    """专家鉴定后的返回结构：包含专家身份背书"""
    
    # 专家专业详情
    expert_pro_fields = {
        'real_name': fields.String,
        'title': fields.String,
        'organization': fields.String,
        'expertise': fields.String
    }

    data_fields = {
        'post_id': fields.Integer(attribute='id'),
        'status': fields.Integer,
        'final_species_name': fields.String,
        'expert_opinion': fields.String,
        # 嵌套专家信息
        'expert_details': fields.Nested(expert_pro_fields, attribute='expert_display_info'),
        'confirm_time': fields.String(attribute='format_e_time') 
    }
    
    return common_fields(data_fields)

def get_ident_detail_fields():

    # 1. 专家身份背书结构
    expert_info_fields = {
        'real_name': fields.String,
        'pro_title': fields.String,
        'organization': fields.String,
        'expertise_field': fields.String
    }

    # 2. 候选标签结构
    candidate_item = {
        'id': fields.Integer,
        'species_name': fields.String,
        'confidence': fields.Float,
        'vote_count': fields.Integer
    }

    # 3. 详情主体结构
    data_fields = {
        'id': fields.Integer,
        'user_id': fields.Integer,
        'nickname': fields.String(attribute='author.nickname'),
        'avatar': fields.String(attribute='author.avatar'),
        
        'image_url': fields.String(attribute='full_image_url'),
        'description': fields.String,
        'status': fields.Integer,
        'upload_time': fields.String(attribute='format_time'),
        'participant_count': fields.Integer,
        
        # 地理位置
        'lat': fields.Float(attribute='location_lat'),
        'lng': fields.Float(attribute='location_lng'),
        'address': fields.String(attribute='location_address'),
        
        # 当前用户的投票状态 (未登录或未投票则为 0)
        'my_vote_id': fields.Integer(default=0),
        
        # 专家鉴定结果及意见
        'final_species_name': fields.String,
        'expert_opinion': fields.String,
        'expert_info': fields.Nested(expert_info_fields, attribute='expert_professional_data', allow_null=True),
        
        # 候选标签列表
        'candidates': fields.List(fields.Nested(candidate_item))
    }

    return common_fields(data_fields)

def op_id_fields():
    """操作成功返回ID"""
    return common_fields({'id': fields.Integer})

def get_species_detail_fields():
    # 1. 定义多媒体子项的结构 (对应新的数据库字段)
    media_item = {
        'media_id': fields.Integer,
        'file_url': fields.String,
        'thumbnail_url': fields.String,
        'title': fields.String,
        # 虽然逻辑在后端分好了类，但返回具体的类型字段方便前端做校验或逻辑判断
        'media_type': fields.String,
        'media_category': fields.String,
        'morphology_type': fields.String,
        'model_category': fields.String
    }

    # 2. 核心业务字段
    data_fields = {
        'species_id': fields.Integer,
        'chinese_name': fields.String(default=''),
        'english_name': fields.String(default=''),
        'species_name': fields.String(default=''),
        'order_name': fields.String(default=''),
        'family_name': fields.String(default=''),
        'nomenclator': fields.String(default=''),
        'naming_year': fields.String(default=''),
        'type_locality': fields.String(default=''),
        'latitude': fields.String(default=''),
        'longitude': fields.String(default=''),
        'domestic_distribution': fields.String(default=''),
        'foreign_distribution': fields.String(default=''),
        'diagnostic_features': fields.String(default=''),
        'references': fields.String(default=''),
        'synonyms': fields.String(default=''),
        'subspecies': fields.String(default=''),
        'c_time': fields.String, 
        'e_time': fields.String,
        
        # 普通展示模块 (所有人可见)
        'normal_media': fields.Nested({
            'images': fields.List(fields.Nested(media_item)),
            'videos': fields.List(fields.Nested(media_item))
        }),
        
        # [形态学信息] 模块 (仅专业人员可见)
        # 使用 allow_null=True，当后端返回 None 时，前端收到 null 而不是结构体
        'morphology_info': fields.Nested({
            'specimen_photos': fields.List(fields.Nested(media_item)), # 对应 标本模型
            'sections': fields.List(fields.Nested(media_item)),        # 对应 切片
            'models_3d': fields.Nested({                               # 对应 三维模型
                'organ': fields.List(fields.Nested(media_item)),       # 对应 器官
                'skeleton': fields.List(fields.Nested(media_item)),    # 对应 骨骼
                'tissue': fields.List(fields.Nested(media_item))       # 对应 组织
            })
        }, allow_null=True)
    }

    # 调用你统一的包装函数
    return common_fields(data_fields)

def get_admin_user_fields():
    """
    专门给管理员管理界面使用的字段定义
    """
    data_fields = {
        'id': fields.Integer,
        'username': fields.String,
        'nickname': fields.String,
        'account_status': fields.String,
        'role_type': fields.String,
        'c_time': fields.Integer,
        'e_time': fields.Integer
    }
    return common_fields(data_fields)

def get_import_result_fields():
    # 失败项的结构
    error_detail = {
        'line': fields.Integer,     # Excel 行号
        'item': fields.String,      # 物种名称标识
        'reason': fields.String     # 失败具体原因
    }
    
    data_fields = {
        'total': fields.Integer,
        'success': fields.Integer,
        'fail': fields.Integer,
        'error_details': fields.List(fields.Nested(error_detail))
    }
    return common_fields(data_fields) # 包装成你统一的 resid/msg 格式

# 审核记录基础字段
audit_base_fields = {
    'audit_id': fields.Integer,
    'applicant_id': fields.String,
    'target_species_id': fields.String,
    'operate_type': fields.String,
    'status': fields.Integer,
    'reject_reason': fields.String,
    'create_time': fields.Integer,
    'audit_time': fields.Integer,
    'auditor_id': fields.Integer
}

def get_audit_list_fields():
    """列表结构：不返回巨大的 snapshot，只返回摘要"""
    data_schema = {
        'audit_list': fields.List(fields.Nested(audit_base_fields)),
        'pagination': fields.Nested({
            'total': fields.Integer,
            'page': fields.Integer,
            'per_page': fields.Integer
        })
    }
    return common_fields(data_schema)

def get_audit_detail_fields():
    """详情结构：包含解析后的内容快照"""
    full_fields = audit_base_fields.copy()
    # 增加 content 字段，对应解析后的 JSON 字典
    full_fields['content'] = fields.Raw 
    return common_fields(full_fields)

def game_user_ranking_fields():
    data_field = {
        'uid': fields.Integer(default=0),
        'score': fields.Integer(default=0),
        'user_name': fields.String(default=''),
        'user_mobile': fields.String(default=''),

    }
    data_fields = {
        'data': fields.List(fields.Nested(data_field))
    }
    return common_fields(data_fields)


def user_history_record_fields():
    level_record_field = {
        'tips': fields.String(default=''),
        'level': fields.Integer(default=0),
        'score': fields.Integer(default=0),
        'is_break': fields.Integer(default=0),
        'error_count': fields.Integer(default=0),
    }

    data_field = {
        'level': fields.Integer(default=0),
        'score': fields.Integer(default=0),
        'level_record': fields.List(fields.Nested(level_record_field))
    }

    data_fields = {
        'user_name': fields.String(default=''),
        'user_mobile': fields.String(default=''),
        'highest_score': fields.Integer(default=0),
        'break_record_count': fields.Integer(default=0),
        'break_level_record': fields.List(fields.Nested(data_field))
    }
    return common_fields(data_fields)


def sign_fields():
    data_fields = {
        'username': fields.String(default=''),
        'auth_token': fields.String(default=''),
        'user_id': fields.Integer(default=0),
        'b_id': fields.Integer(default=0),
    }
    return common_fields(data_fields)


def user_game_fields():
    data_fields = {
        'data': fields.List(fields.String),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def games_fields():
    data_field = {
        'game_name': fields.String(default=''),
        'id': fields.String(default=''),
        'user_count': fields.Integer(default=0),
    }
    data_fields = {
        'data': fields.List(fields.Nested(data_field)),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def game_users_fields():
    data_field = {
        'user_name': fields.String(default=''),
        'user_mobile': fields.String(default=''),
        'game_name': fields.String(default=''),
        'highest_score': fields.Integer(default=0),
        'user_id': fields.Integer(default=0),
        'break_count': fields.Integer(default=0),
        'start_time': fields.String(default=''),
        'end_time': fields.String(default=''),
        'c_time': fields.String(default=''),
        'game_id': fields.String(default=''),
    }

    data_fields = {
        'data': fields.List(fields.Nested(data_field)),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def label_fields():
    data_field = {
        'name': fields.String(default=''),
        'id': fields.Integer(default=0),
    }

    data_fields = {
        'data': fields.List(fields.Nested(data_field)),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def article_fields():
    data_field = {
        'title': fields.String(default=''),
        'instruction': fields.String(default=''),
        'id': fields.Integer(default=0),
        'c_time': fields.String(default=''),
        'label_name': fields.String(default=''),
        'label_id': fields.Integer(default=0),
    }

    data_fields = {
        'data': fields.List(fields.Nested(data_field)),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def article_info_fields():
    data_field = {
        'title': fields.String(default=''),
        'content': fields.String(default=''),
        'label_name': fields.String(default=''),
        'label_id': fields.Integer(default=0),
        'id': fields.Integer(default=0),
        'c_time': fields.String(default=''),
    }
    data_fields = {
        'data': fields.Nested(data_field),
    }
    return common_fields(data_fields)


def answer_record_user_fields():
    data_field = {
        'questionnaire_name': fields.String(default=''),
        'id': fields.Integer(default=0),
        'score': fields.Integer(default=0),
        'c_time': fields.String(default=''),
        'feedback_content': fields.String(default=''),
        'user_name': fields.String(default=''),
    }

    data_fields = {
        'data': fields.List(fields.Nested(data_field)),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def user_basic_information_fields():
    data_field = {
        "name": fields.String(default=''),
        "gender": fields.String(default=''),
        "nation": fields.String(default=''),
        "birthday": fields.String(default=''),
        "culture": fields.String(default=''),
        "marriage": fields.String(default=''),
        "live": fields.String(default=''),
        "work_status": fields.String(default=''),
        "position": fields.String(default=''),
        "economy": fields.String(default=''),
        "address": fields.String(default=''),
        "internet_equipment": fields.String(default=''),
        "internet_time": fields.String(default=''),
        "social_media": fields.String(default=''),
        "height": fields.String(default=''),
        "weight": fields.String(default=''),
        "id_card": fields.String(default=''),
        "group_id": fields.String(default=''),
        "age": fields.Integer(default=0),
        "nickname": fields.String(default=''),
        "avatar_url": fields.String(default=''),
        "province": fields.String(default=''),
        "city": fields.String(default=''),
        "district": fields.String(default=''),
        "basic_diseases": fields.String(default=''),
        "serious_illness": fields.String(default=''),
            "RDAs_diary": fields.String(default='')


    }

    data_fields = {
        'data': fields.Nested(data_field),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def sport_evaluation_fields():
    data_field = {
        'user_name': fields.String(default=''),
        'c_time': fields.String(default=''),
        'height': fields.Float(default=0.0),
        'weight': fields.Float(default=0.0),
        'sit_and_reach_l': fields.Float(default=0.0),
        'sit_and_reach_r': fields.Float(default=0.0),
        'claw_l': fields.Float(default=0.0),
        'claw_r': fields.Float(default=0.0),
        'sitting_count': fields.Integer(default=0),
        'arm_count_l': fields.Integer(default=0),
        'arm_count_r': fields.Integer(default=0),
        'mark_time_count': fields.Integer(default=0),
        'walk244': fields.Integer(default=0),
        'id': fields.Integer(default=0),
        'user_id': fields.Integer(default=0),
        'mark_time_score': fields.Float(default=0),
        'mark_time_level': fields.String(default=''),
        'sitting_level': fields.String(default=''),
        'sitting_score': fields.Float(default=0),
        'arm_score': fields.Float(default=0),
        'arm_level': fields.String(default=''),
        'BMI_score': fields.Float(default=0),
        'BMI_level': fields.String(default=''),
        'walk244_score': fields.Float(default=0),
        'walk244_level': fields.String(default=''),
        'sit_and_reach_score': fields.Float(default=0),
        'sit_and_reach_level': fields.String(default=''),
        'claw_score': fields.Float(default=0),
        'claw_level': fields.String(default=''),
        'total_points': fields.Float(default=0)
    }

    data_fields = {
        'data': fields.Nested(data_field),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def user_diet_fields():
    data_field = {

        "time": fields.String(default=''),
        "water": fields.String(default=''),
        "cereal": fields.String(default=''),
        "tubers": fields.String(default=''),
        "vegetable": fields.String(default=''),
        "fruit": fields.String(default=''),
        "meat_egg": fields.String(default=''),
        "milk": fields.String(default=''),
        "soy_nut": fields.String(default=''),
        "salt": fields.String(default=''),
        "oil": fields.String(default='')

    }

    data_fields = {
        'data': fields.Nested(data_field),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def professor_fields():
    data_fields = {
        'id': fields.Integer(default=0),
        'professor_name': fields.String(default=''),
        'auth_token': fields.String(default=''),
        'email': fields.String(default=''),
        'organization': fields.String(default=''),
        'professor_status': fields.String(default=''),
    }
    return common_fields(data_fields)


def admin_fields():
    data_fields = {
        'admin_id': fields.String(default=''),
        'auth_token': fields.String(default=''),
        'username': fields.String(default='')
    }
    return common_fields(data_fields)

def get_admin_list_fields():
    # 定义管理员简单字段
    admin_simple_fields = {
        'admin_id': fields.Integer,
        'username': fields.String(default=''),
        'real_name': fields.String(default=''),
        'status': fields.String(default=''),
        'last_login': fields.String(default='')
    }
    
    # 定义统计信息字段
    stats_fields = {
        'total_count': fields.Integer(default=0),
        'active_count': fields.Integer(default=0),
        'disabled_count': fields.Integer(default=0),
        'wait_count': fields.Integer(default=0)
    }
    
    # 定义完整的数据字段
    data_fields = {
        'admins': fields.List(fields.Nested(admin_simple_fields)),
        'total': fields.Integer(default=0),
        'page': fields.Integer(default=1),
        'per_page': fields.Integer(default=10),
        'stats': fields.Nested(stats_fields)
    }
    
    # 返回 common_fields 包装的字段
    return common_fields(data_fields)

def get_species_list_fields():

    data_fields = {
        'species_id': fields.Integer,
        'chinese_name': fields.String(default=''),
        'species_name': fields.String(default=''),
        'order_name': fields.String(default=''),
        'family_name': fields.String(default=''),
        'cover_image': fields.String(default='') # 封面图
    }
    # 包装的分页结构
    list_schema = {
        'species_list': fields.List(fields.Nested(data_fields)),
        'pagination': fields.Nested({
            'total': fields.Integer,
            'page': fields.Integer,
            'per_page': fields.Integer
        })
    }
    return common_fields(list_schema)


def audit_list_fields():
    """
    定义审核列表的返回数据结构
    """
    
    # 1. 单条审核记录的字段结构
    audit_item = {
        'audit_id': fields.Integer,
        'applicant_id': fields.String,       # 申请人ID
        'operate_type': fields.String,       # add 或 update
        'target_species_id': fields.String,  # 目标物种ID
        'status': fields.Integer,            # 0, 1, 2
        'reject_reason': fields.String,      # 驳回原因
        'create_time': fields.Integer,       # 创建时间
        'audit_time': fields.Integer,        # 审核时间
        'auditor_id': fields.Integer,        # 审核人ID
        'content_snapshot': fields.Raw       # 【关键】使用 Raw 类型，原样返回字典数据
    }

    # 2. 分页信息结构
    pagination = {
        'total': fields.Integer,
        'page': fields.Integer,
        'per_page': fields.Integer,
        'pages': fields.Integer
    }

    # 3. 组合 data 数据
    data_fields = {
        'audit_list': fields.List(fields.Nested(audit_item)), # 列表嵌套
        'pagination': fields.Nested(pagination)               # 对象嵌套
    }

    # 4. 返回完整结构 (common_fields 应该在文件上方已定义或导入)
    return common_fields(data_fields)
