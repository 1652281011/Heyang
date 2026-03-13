import time
from .base import db, Base

class Post(Base):
    """帖子主表"""
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False, comment='完整内容')
    
    # 计数器冗余字段（提升列表页性能）
    view_count = db.Column(db.Integer, default=0, comment='阅读数')
    like_count = db.Column(db.Integer, default=0, comment='点赞数')
    comment_count = db.Column(db.Integer, default=0, comment='评论数')
    
    # 关联：帖子下的图片和评论
    images = db.relationship('PostImage', backref='post', lazy='dynamic')
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def to_summary_dict(self):
        """
        核心逻辑：社区列表预览模式
        只返回标题、摘要和第一张图片URL
        """
        time_struct = time.localtime(self.create_time)
        formatted_time = time.strftime('%Y-%m-%d', time_struct)
        first_img = PostImage.query.filter_by(post_id=self.id).first()
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.content[:80] + "..." if len(self.content) > 80 else self.content,
            "cover": first_img.url if first_img else None,
            "counts": {
                "view": self.view_count,
                "like": self.like_count,
                "comment": self.comment_count
            },
            "create_time": formatted_time
        }

    def to_full_dict(self):
        """
        核心逻辑：进入详情页模式
        返回完整内容和所有图片、评论
        """
        time_struct = time.localtime(self.create_time)
        formatted_time = time.strftime('%Y-%m-%d', time_struct)
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "images": [img.url for img in self.images],
            "counts": {
                "view": self.view_count,
                "like": self.like_count
            },
            "author": self.author.nickname if self.author else "匿名用户",
            "create_time": formatted_time
        }

class PostImage(Base):
    """帖子图片表"""
    __tablename__ = 'post_image'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)

class Comment(Base):
    """帖子评论表"""
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def to_dict(self):
        from .users import User
        user = User.query.get(self.user_id)
        
        # 这里的 self.create_time 是整数
        ts = self.create_time if self.create_time else int(time.time())
        formatted_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(ts))
        
        return {
            "id": self.id,
            "username": user.nickname if user else "匿名",
            "content": self.content,
            "create_time": formatted_time
        }

class Like(Base):
    """点赞记录表"""
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # 联合唯一索引：确保一个用户只能点赞一次
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='_user_post_like_uc'),)