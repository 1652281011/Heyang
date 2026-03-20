#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 下午11:03
# @Software：PyCharm
# @Author  : scott

# from app.api.v1.apps.admin_auth.admin_audit import SpeciesAuditActionResource
from app.api.v1.apps.admin_auth.admin_audit import SpeciesAuditActionResource
from app.api.v1.apps.admin_auth.admin_register import AdminRegister
from app.api.v1.apps.admin_auth.admin_sign_in import AdminSignIn
from app.api.v1.apps.admin_auth.professional_audit import ProfessionalAuditResource
from app.api.v1.apps.admin_auth.professional_audit_detail import ProfessionalDetailResource
from app.api.v1.apps.admin_auth.professional_audit_list import ProfessionalListResource
from app.api.v1.apps.admin_auth.get_admin_list import GetAdminList
from app.api.v1.apps.admin_auth.update_admin_status import UpdateAdminStatus
from app.api.v1.apps.community.mylikepost import MyLikedPostResource
from app.api.v1.apps.community.mypostlist import MyPostListResource
from app.api.v1.apps.community.post_comment import CommentResource
from app.api.v1.apps.community.post_delete import PostDeleteResource
from app.api.v1.apps.community.post_detail import PostDetailResource
from app.api.v1.apps.community.post_like import LikeResource
from app.api.v1.apps.community.post_list import PostListResource
from app.api.v1.apps.community.post_publish import PostPublish
from app.api.v1.apps.community.post_update import PostUpdateResource
from app.api.v1.apps.datetime.datetime import DateTime
# from app.api.v1.apps.break_record.break_record import BreakRecord, GameUserRanking, UsersHistoryRecord, \
#     UsersHistoryRecordInfo




from app.api.v1.apps.professor.apply import ProfessionalApplyResource

from app.api.test import Test1
from app.api.v1.apps.professor.audit_progress import MyProfessionalStatusResource
from app.api.v1.apps.professor.species_upload import SpeciesUploadResource
from app.api.v1.apps.species.species_search import GetSpeciesList
from app.api.v1.apps.user.register import Register
from app.api.v1.apps.user.sign_in import SignIn
from app.api.v1.apps.user.update_info import UserInfoResource
from app.api.v1.apps.user.update_password import UserPasswordResource
from app.api.v1.apps.user.user_info import UserFullInfoResource

RESOURCES = [
    (Test1, '/v1/test'),

    (DateTime, '/v1/date-time'),#获取服务器的时间

    #用户信息操作
    (Register, '/v1/user/register'),
    (SignIn, '/v1/user/sign-in'),
    (UserInfoResource, '/v1/user/updinfo'),
    (UserPasswordResource, '/v1/user/updpwd'),
    (UserFullInfoResource, '/v1/user/info'),
    
    (AdminRegister, '/v1/admin/register'),
    (AdminSignIn, '/v1/admin/sign-in'),

    (GetAdminList, '/v1/admin/getadminlist'),

    (UpdateAdminStatus, '/v1/admin/updateadminstatus'),
    (ProfessionalListResource, '/v1/admin/pro_list'),
    (ProfessionalAuditResource, '/v1/admin/professionalaudit'),
    (ProfessionalDetailResource, '/v1/admin/prodetail'),

    (ProfessionalApplyResource, '/v1/professor/apply'),
    (MyProfessionalStatusResource, '/v1/professor/audit'),

    (GetSpeciesList, '/v1/species/list'),

    (SpeciesAuditActionResource, '/v1/admin/speciesaudit'),
    (SpeciesUploadResource, '/v1/professor/speciesupload'),

    (PostListResource, '/v1/community/postlist'),
    (PostPublish, '/v1/community/postpublish'),
    (PostDeleteResource,'/v1/community/postdelete'),
    (PostUpdateResource, '/v1/community/postupdate'),
    (PostDetailResource, '/v1/community/postdetail'),
    (MyPostListResource, '/v1/community/myposts'),
    (MyLikedPostResource, '/v1/community/myliked'),
    (LikeResource, '/v1/community/like'),
    (CommentResource, '/v1/community/comment')
]
