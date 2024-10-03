from app.extensions import db
from app.models.post import Post, PostMedia, PostDescription, PostComment


def create_post(title, media_list):
    media = []
    for media_item in media_list:
        description = None
        if media_item['description']:
            description = PostDescription(
                content=media_item['description']
            )

        media.append(
            PostMedia(
                media_url=media_item['media_url'],
                description=description
            )
        )


    # TODO: check if failed because of post_id collision
    # TODO: generate proper thumbnail
    post = Post(title, media, media[0].media_url)
    db.session.add(post)
    db.session.commit()
    return post


def _rows_to_dicts(rows):
    return tuple(row._asdict() for row in rows)


def get_posts():
    result = db.session.execute(
        db.select(
            Post.post_id,
            Post.title,
            Post.thumbnail_url,
            Post.created_on,
            Post.updated_on,
            Post.score,
            Post.comment_count,
            Post.views,
        )
    )
    return _rows_to_dicts(result)


def get_post_media(post_id):
    result = db.session.execute(
        db.select(
            PostMedia.media_url,
            PostDescription.content.label('description')
        ).outerjoin(PostDescription).where(PostMedia.post_id == post_id)
    )
    return _rows_to_dicts(result)


def get_post_and_media(post_id):
    post = db.session.execute(
        db.select(Post)
        .options(
            db.selectinload(Post.media).selectinload(PostMedia.description)
        ).where(Post.post_id == post_id)
    ).scalars().one_or_none()

    if not post:
        return None

    media = tuple(
        {
            'media_url': media_item.media_url,
            'description': media_item.description.content
                if media_item.description else None
        } for media_item in post.media
    )

    result = {
        'post_id': post.post_id,
        'title': post.title,
        'created_on': post.created_on,
        'updated_on': post.updated_on,
        'score': post.score,
        'views': post.views,
        'comment_count': post.comment_count,
        'media': media,
        'thumbnail_url': post.thumbnail_url,
    }
    return result


def get_post_comments(post_id):
    result = db.session.execute(
        db.select(
            PostComment.content,
            PostComment.score,
            PostComment.created_on,
        ).where(PostComment.post_id == post_id)
    )
    return _rows_to_dicts(result)


def increment_post_views(post_id):
    db.session.execute(
        db.update(Post)
            .where(Post.post_id == post_id)
            .values(views=Post.views + 1)
    )
    db.session.commit()

