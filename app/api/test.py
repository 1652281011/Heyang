#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 下午11:05
# @Software：PyCharm
# @Author  : scott


from datetime import datetime, timedelta, date, time
from flask import current_app
from flask_restful import Resource

from app import db
from app.api.common.fields import test_fields
from app.api.common.parser import test_parser
from app.api.common.response import success


from app.models.users import User


from flask import current_app, g, request, jsonify
from app.utils.decorators import login_required



class Test1(Resource):
    # @login_required
    def get(self):
        return jsonify({"status": 'ok!'})

    def post(self):
        args = test_parser()

        # for k, v in args.items():
        #     print(f'{k}: {v}')
        pw='error'
        pw=User.generation_password(args.get('pw'))
        data = {
            'data': pw
        }

        return success(data=data, data_fileds=test_fields())

