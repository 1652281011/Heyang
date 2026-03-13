from .base import db, Base

class User(Base):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(50), nullable=False, comment='用户昵称')
    avatar = db.Column(db.String(255), comment='用户头像URL')
    bio = db.Column(db.String(255), comment='个人简介')
    
    # 关联关系：一个用户可以发多篇帖子
    posts = db.relationship('Post', backref='author', lazy='dynamic')