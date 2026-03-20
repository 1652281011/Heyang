from app.models import db
from app.models.community import Post, Like, Comment
from app.models.users import User

class InteractService:
    @staticmethod
    def toggle_like(post_id, user_id):
        post = Post.query.get(post_id)
        if not post: return False, "帖子不存在"
        
        # 获取帖子作者对象
        author = User.query.get(post.user_id)
        
        like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        
        try:
            if like:
                # 取消点赞
                db.session.delete(like)
                post.like_count = max(0, post.like_count - 1)
                # 同步减少作者的总获赞数
                if author:
                    author.total_like_count = max(0, author.total_like_count - 1)
                res = "unliked"
            else:
                # 新增点赞
                db.session.add(Like(post_id=post_id, user_id=user_id))
                post.like_count += 1
                # 同步增加作者的总获赞数
                if author:
                    author.total_like_count += 1
                res = "liked"
            
            db.session.commit()
            return True, {"action": res, "count": post.like_count}
        except Exception as e:
            db.session.rollback()
            return False, "操作失败"

    @staticmethod
    def add_comment(post_id, user_id, content):
        post = Post.query.get(post_id)
        if not post: return False, "帖子不存在"
        comment = Comment(post_id=post_id, user_id=user_id, content=content)
        post.comment_count += 1
        db.session.add(comment)
        db.session.commit()
        return True, comment.to_dict()