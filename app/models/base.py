#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/27 下午10:45
# @Software：PyCharm
# @Author  : scott
from datetime import datetime
import time
from app.models import db
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy


class BaseModel:
    # # 注册时间
    # c_time = db.Column(db.DateTime, server_default=func.now())
    # # 更新时间
    # e_time = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    __abstract__ = True
    c_time = db.Column(db.Integer, default=lambda: int(time.time()))
    e_time = db.Column(db.Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))

class Base(db.Model):
    """
    模型基类：为所有表提供基础字段
    __abstract__ = True 表示这是一类抽象模型，不会在数据库中生成对应的表
    """
    __abstract__ = True
    
    # 状态码：1-正常, 0-已删除, -1-待审核等
    status = db.Column(db.SmallInteger, default=1)
    # 创建时间
    create_time = db.Column(db.Integer, default=lambda: int(time.time()))
    # 最后更新时间
    update_time = db.Column(db.Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))

    def delete(self):
        """逻辑删除"""
        self.status = 0