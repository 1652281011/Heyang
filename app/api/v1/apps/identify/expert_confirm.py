# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource, reqparse
from app.api.common.response import success, error
from app.api.common.fields import op_id_fields
from app.models.species import SpeciesPost, SpeciesCandidate
from app.models.users import User
from app.models.base import db

class SpeciesExpertConfirm(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('post_id', type=int, required=True, location='json')
        parser.add_argument('candidate_id', type=int, required=True, location='json')
        args = parser.parse_args()

        auth_token = request.headers.get('Authorization')
        user = User.verify_auth_token(auth_token)
        if not user or user.role_type not in ['2']:
            return error(resid=403, msg='权限不足')

        post = SpeciesPost.query.get(args['post_id'])
        cand = SpeciesCandidate.query.get(args['candidate_id'])
        try:
            post.status = 1
            post.final_species_id = cand.id
            post.final_species_name = cand.species_name
            post.confirmed_by = user.id
            db.session.commit()
            return success(msg='已确认结果', data={'id': post.id}, data_fileds=op_id_fields())
        except Exception:
            db.session.rollback()
            return error(msg='操作异常')