#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/29 上午12:01
# @Software：PyCharm
# @Author  : scott
from flask_restful import fields


def common_fields(data_fields=None):
    """
    通用字段封装
    :param data_fields: 具体的业务数据字段结构 (Dict 或 List)
    """
    # 1. 定义基础字段
    resource_fields = {
        'resid': fields.Integer(default=200),
        'msg': fields.String(default='success'),
        'status': fields.String(default='success'),
        'data': fields.Raw(default=None)  # 默认 data 为空，使用 Raw 防止被忽略
    }

    # 2. 如果传入了 data_fields，则覆盖 data 字段的定义
    if data_fields:
        # 如果传入的是字典，通常需要用 Nested 包裹
        if isinstance(data_fields, dict):
            resource_fields['data'] = fields.Nested(data_fields)
        # 如果传入的已经是字段对象（如 fields.List），直接赋值
        else:
            resource_fields['data'] = data_fields

    return resource_fields

def test_fields():
    data_fields = {
        'data': fields.String
    }
    return common_fields(data_fields)


def user_fields():
    data_field = {
        'id': fields.Integer(default=0),
        'name': fields.String(default=''),
        'mobile': fields.String(default=''),
        'ctime': fields.String(default=''),
        'auth_token': fields.String(default='')
    }

    data_fields = {
        'data': fields.Nested(data_field),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


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

    species_item_fields = {
        'species_id': fields.String(default=''),
        'chinese_name': fields.String(default=''),
        'english_name': fields.String(default=''),
        'species': fields.String(default=''),
        'order_name': fields.String(default=''),
        'family': fields.String(default=''),
        'collection_province': fields.String(default=''),
        'scientific_name': fields.String(default=''),
        'grade': fields.String(default=''),
        'description': fields.String(default=''),
        'distribution': fields.String(default=''),
        'epidemic': fields.String(default=''),
        'sequense': fields.String(default='')
    }

    pagination_fields = {
        'total': fields.Integer(default=0),
        'page': fields.Integer(default=1),
        'per_page': fields.Integer(default=20),
        'pages': fields.Integer(default=0)
    }

    data_fields = {
        'species_list': fields.List(fields.Nested(species_item_fields)),
        'pagination': fields.Nested(pagination_fields)
    }

    return common_fields(data_fields)


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
