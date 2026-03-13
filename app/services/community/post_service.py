from app.models import db
from app.models.community import Post, PostImage
from app.utils.uploader import save_upload_file

class PostService:
    @staticmethod
    def get_list(keyword, page, per_page):
        query = Post.query.filter_by(status=1)
        if keyword:
            query = query.filter(Post.title.contains(keyword))
        pagination = query.order_by(Post.create_time.desc()).paginate(page=page, per_page=per_page)
        return {"total": pagination.total, "items": [p.to_summary_dict() for p in pagination.items]}

    @staticmethod
    def create_post(args):
        try:
            post = Post(title=args['title'], content=args['content'], user_id=args['user_id'])
            db.session.add(post)
            db.session.flush()
            if args['images']:
                for img in args['images']:
                    url = save_upload_file(img)
                    if url: db.session.add(PostImage(post_id=post.id, url=url))
            db.session.commit()
            return True, post.id
        except Exception as e:
            db.session.rollback()
            return False, str(e)