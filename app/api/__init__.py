#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 下午11:03
# @Software：PyCharm
# @Author  : scott

# from app.api.v1.apps.admin_auth.admin_audit import SpeciesAuditActionResource
from app.api.v1.apps.admin_auth.add_species import SpeciesAddResource
from app.api.v1.apps.admin_auth.admin_account import AdminAccountManage
from app.api.v1.apps.admin_auth.audit_list import AdminAuditList
from app.api.v1.apps.admin_auth.professional_audit import ProfessionalAuditResource
from app.api.v1.apps.admin_auth.professional_audit_detail import ProfessionalDetailResource
from app.api.v1.apps.admin_auth.professional_audit_list import ProfessionalListResource
from app.api.v1.apps.admin_auth.species_audit import SpeciesAuditActionResource

from app.api.v1.apps.admin_auth.species_media_manage import MediaManageApi
from app.api.v1.apps.admin_auth.specise_edit import SpeciesEditResource
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




from app.api.v1.apps.identify.ai_ident import SpeciesAIPreview
from app.api.v1.apps.identify.delete import SpeciesPostDelete
from app.api.v1.apps.identify.expert_confirm import ExpertConfirmAction
from app.api.v1.apps.identify.mypost import MySpeciesPostList
from app.api.v1.apps.identify.post_detail import SpeciesPostDetail
from app.api.v1.apps.identify.post_identify import SpeciesPostAction
from app.api.v1.apps.identify.post_list import SpeciesPostList
from app.api.v1.apps.identify.species_vote import SpeciesVoteAction
from app.api.v1.apps.identify.voted_post import MyVotedSpeciesPostList
from app.api.v1.apps.professor.apply import ProfessionalApplyResource

from app.api.test import Test1
from app.api.v1.apps.professor.audit_progress import MyProfessionalStatusResource
from app.api.v1.apps.professor.edit_species_audit import ExpertModifyAuditResource
from app.api.v1.apps.professor.species_audit_detail import SpeciesAuditDetail
from app.api.v1.apps.professor.species_audit_list import ExpertAuditList
from app.api.v1.apps.professor.species_upload import SpeciesUploadResource
from app.api.v1.apps.species.detail import GetSpeciesDetail
from app.api.v1.apps.species.species_import import SpeciesImportResource
from app.api.v1.apps.species.species_search import GetSpeciesList
from app.api.v1.apps.user.register import Register, SendCode
from app.api.v1.apps.user.reset_password import ResetPassword
from app.api.v1.apps.user.sign_in import SignIn
from app.api.v1.apps.user.update_info import UserInfoResource
from app.api.v1.apps.user.update_password import UserPasswordResource
from app.api.v1.apps.user.user_info import UserFullInfoResource
from app.api.v1.apps.user.wx_login import WXLoginResource

RESOURCES = [
    (Test1, '/v1/test'),

    (DateTime, '/v1/date-time'),#获取服务器的时间

    #用户信息操作
    (SendCode, '/v1/user/email_code'),
    (Register, '/v1/user/register'),
    (SignIn, '/v1/user/sign-in'),
    (UserInfoResource, '/v1/user/updinfo'),
    (UserPasswordResource, '/v1/user/updpwd'),
    (ResetPassword, '/v1/user/resetpwd'),
    (UserFullInfoResource, '/v1/user/info'),

    (WXLoginResource, '/v1/user/wx_login'),
    
    # (AdminRegister, '/v1/admin/register'),
    # (AdminSignIn, '/v1/admin/sign-in'),

    # # (GetAdminList, '/v1/admin/getadminlist'),

    # (UpdateAdminStatus, '/v1/admin/updateadminstatus'),
    (ProfessionalListResource, '/v1/admin/pro_list'),
    (ProfessionalAuditResource, '/v1/admin/professionalaudit'),
    (ProfessionalDetailResource, '/v1/admin/prodetail'),
    (AdminAccountManage, '/v1/admin/manage'),

    (ProfessionalApplyResource, '/v1/professor/apply'),
    (MyProfessionalStatusResource, '/v1/professor/audit'),

    (GetSpeciesDetail, '/v1/species/detail'),
    (GetSpeciesList, '/v1/species/list'),

    (SpeciesEditResource, '/v1/admin/species/edit'),
    (MediaManageApi, '/v1/admin/species/media'),
    (SpeciesAddResource, '/v1/admin/species/add'),
    (SpeciesImportResource, '/v1/admin/species/batchimport'),

    (AdminAuditList, 'v1/admin/species/audit/list'),
    (SpeciesAuditActionResource, '/v1/admin/speciesaudit'),
    (SpeciesUploadResource, '/v1/professor/speciesupload'),
    (ExpertAuditList, '/v1/professor/species/audit/list'),
    (SpeciesAuditDetail, '/v1/species/audit/detail'),
    (ExpertModifyAuditResource, '/v1/professor/edit/audit'),

    (PostListResource, '/v1/community/postlist'),
    (PostPublish, '/v1/community/postpublish'),
    (PostDeleteResource,'/v1/community/postdelete'),
    (PostUpdateResource, '/v1/community/postupdate'),
    (PostDetailResource, '/v1/community/postdetail'),
    (MyPostListResource, '/v1/community/myposts'),
    (MyLikedPostResource, '/v1/community/myliked'),
    (LikeResource, '/v1/community/like'),
    (CommentResource, '/v1/community/comment'),

    (SpeciesAIPreview, '/v1/identify/aiprevew'),
    (SpeciesPostAction, '/v1/identify/post'),
    (SpeciesPostList, '/v1/identify/list'),
    (SpeciesVoteAction, '/v1/identify/vote'),
    (ExpertConfirmAction, '/v1/identify/confirm'),
    (SpeciesPostDetail, '/v1/identify/detail'),
    (MySpeciesPostList, '/v1/identify/mypost'),
    (MyVotedSpeciesPostList, '/v1/identify/myvoted'),
    (SpeciesPostDelete, '/v1/identify/delete')
]
