#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 下午11:03
# @Software：PyCharm
# @Author  : scott

from app.api.v1.apps.admin_auth.admin_audit import SpeciesAuditActionResource
from app.api.v1.apps.admin_auth.admin_register import AdminRegister
from app.api.v1.apps.admin_auth.admin_sign_in import AdminSignIn
from app.api.v1.apps.admin_auth.audit_action import AdminAuditAction
from app.api.v1.apps.admin_auth.audit_list import AdminAuditList
from app.api.v1.apps.admin_auth.get_admin_list import GetAdminList
from app.api.v1.apps.admin_auth.update_admin_status import UpdateAdminStatus
from app.api.v1.apps.community.post_comment import CommentResource
from app.api.v1.apps.community.post_detail import PostDetailResource
from app.api.v1.apps.community.post_like import LikeResource
from app.api.v1.apps.community.post_list import PostListResource
from app.api.v1.apps.community.post_publish import PostPublishResource
from app.api.v1.apps.datetime.datetime import DateTime
# from app.api.v1.apps.break_record.break_record import BreakRecord, GameUserRanking, UsersHistoryRecord, \
#     UsersHistoryRecordInfo




from app.api.v1.apps.professor.professor_sign_in import ProfessorSignIn
from app.api.v1.apps.professor.professor_sign_up import ProfessorSignUp

from app.api.test import Test1
from app.api.v1.apps.professor.species_upload import SpeciesUploadResource
from app.api.v1.apps.species.species_search import GetSpeciesList

RESOURCES = [
    (Test1, '/v1/test'),

    (DateTime, '/v1/date-time'),#获取服务器的时间
    
    (AdminRegister, '/v1/admin/register'),
    (AdminSignIn, '/v1/admin/sign-in'),

    (GetAdminList, '/v1/admin/getadminlist'),

    (UpdateAdminStatus, '/v1/admin/updateadminstatus'),


    (ProfessorSignIn, '/v1/professor/sign-in'),
    (ProfessorSignUp, '/v1/professor/sign-up'),

    (GetSpeciesList, '/v1/species/getspecieslist'),

    (SpeciesAuditActionResource, '/v1/admin/speciesaudit'),
    (SpeciesUploadResource, '/v1/professor/speciesupload'),

    (AdminAuditList, '/v1/admin/audit_list'),
    (AdminAuditAction, '/v1/admin/audit_action'),

    (PostListResource, '/v1/community/postlist'),
    (PostPublishResource, '/v1/community/postpublish'),
    (PostDetailResource, '/v1/community/postdetail'),
    (LikeResource, '/v1/community/like'),
    (CommentResource, '/v1/community/comment')
]
