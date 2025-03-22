from enum import Enum

from app.extensions import db
from app.models.post import Post, PostMedia, PostDescription, PostComment


POSTS_PER_PAGE = 20

def create_post(title, media_list, is_public):
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
    post = Post(title, media, media_list[0]['thumbnail_url'], is_public)
    db.session.add(post)
    db.session.commit()
    return {
        'post_id':       post.post_id,
        'title':         post.title,
        'thumbnail_url': post.thumbnail_url,
        'created_on':    post.created_on,
        'updated_on':    post.updated_on,
        'score':         post.score,
        'comment_count': post.comment_count,
        'views':         post.views,
        'is_public':     post.is_public,
    }


def comment_on_post(post_id, content):
    comment = PostComment(content)
    comment.post_id = post_id
    comment.parent_id = None

    db.session.add(comment)
    _increment_post_comment_count(post_id)
    db.session.commit()

    return {
        # TODO: return PK id or an uuid?
        'id': comment.id,
        'parent_id': comment.parent_id,
        'reply_count': comment.reply_count,
        'content': comment.content,
        'score': comment.score,
        'created_on': comment.created_on,
        'post_id': comment.post_id,
    }


def reply_to_comment(post_id, comment_id, content):
    reply = PostComment(content)
    reply.post_id = post_id
    reply.parent_id = comment_id

    db.session.add(reply)
    _increment_post_comment_count(post_id)
    _increment_comment_reply_count(post_id, comment_id)
    db.session.commit()

    return {
        # TODO: return PK id or an uuid?
        'id': reply.id,
        'parent_id': reply.parent_id,
        'reply_count': reply.reply_count,
        'content': reply.content,
        'score': reply.score,
        'created_on': reply.created_on,
        'post_id': reply.post_id,
        'parent_id': reply.parent_id,
    }


def _rows_to_dicts(rows):
    return tuple(row._asdict() for row in rows)


class PostSorting(Enum):
    NEWEST = 'newest'
    TOP = 'top'


def get_public_posts_by_page(page, sorting):
    statement = db.select(
            Post.post_id,
            Post.title,
            Post.thumbnail_url,
            Post.created_on,
            Post.updated_on,
            Post.score,
            Post.comment_count,
            Post.views,
        ).where(
            Post.is_public == True
        )

    match sorting:
        case PostSorting.NEWEST:
            statement = statement.order_by(Post.created_on.desc())
        case PostSorting.TOP:
            statement = statement.order_by(
                Post.score.desc(),
                Post.created_on.desc(),
            )

    statement = statement.limit(
            POSTS_PER_PAGE
        ).offset(
            page*POSTS_PER_PAGE
        )

    result = db.session.execute(statement)
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


class CommentSorting(Enum):
    NEWEST = 'newest'
    MOST_LIKED = 'most-liked'
    OLDEST = 'oldest'


def get_post_comments(post_id, sorting):
    statement = db.select(
            PostComment.id,
            PostComment.content,
            PostComment.parent_id,
            PostComment.reply_count,
            PostComment.score,
            PostComment.created_on,
        ).where(
            PostComment.post_id == post_id,
            PostComment.parent_id == None, # don't include replies
        )

    match sorting:
        case CommentSorting.NEWEST:
            statement = statement.order_by(PostComment.created_on.desc())
        case CommentSorting.MOST_LIKED:
            statement = statement.order_by(
                PostComment.score.desc(),
                PostComment.created_on.desc(),
            )
        case CommentSorting.OLDEST:
            statement = statement.order_by(
                PostComment.created_on.asc(),
            )

    result = db.session.execute(statement)
    return _rows_to_dicts(result)


def get_comment_replies(post_id, comment_id, sorting):
    statement = db.select(
            PostComment.id,
            PostComment.content,
            PostComment.parent_id,
            PostComment.reply_count,
            PostComment.score,
            PostComment.created_on,
        ).where(
            PostComment.post_id == post_id,
            PostComment.parent_id == comment_id,
        )

    match sorting:
        case CommentSorting.NEWEST:
            statement = statement.order_by(PostComment.created_on.desc())
        case CommentSorting.MOST_LIKED:
            statement = statement.order_by(
                PostComment.score.desc(),
                PostComment.created_on.desc(),
            )
        case CommentSorting.OLDEST:
            statement = statement.order_by(
                PostComment.created_on.asc(),
            )

    result = db.session.execute(statement)
    return _rows_to_dicts(result)


def increment_post_views(post_id):
    db.session.execute(
        db.update(Post)
            .where(Post.post_id == post_id)
            .values(views=Post.views + 1)
    )
    db.session.commit()


def _increment_post_comment_count(post_id):
    db.session.execute(
        db.update(Post)
            .where(Post.post_id == post_id)
            .values(comment_count=Post.comment_count + 1)
    )


def _increment_comment_reply_count(post_id, comment_id):
    db.session.execute(
        db.update(PostComment)
            .where(
                PostComment.id == comment_id,
                PostComment.post_id == post_id,
            ).values(
                reply_count=PostComment.reply_count + 1
            )
    )


class Vote(Enum):
    UPVOTE = 1
    DOWNVOTE = -1


def vote_post(post_id, vote):
    if vote not in Vote:
        raise TypeError('vote must be of Vote type.')

    # TODO: check if already voted, and if so, undo vote

    db.session.execute(
        db.update(Post)
            .where(Post.post_id == post_id)
            .values(score=Post.score + vote.value)
    )
    db.session.commit()


def vote_comment(post_id, comment_id, vote):
    if vote not in Vote:
        raise TypeError('vote must be of Vote type.')

    # TODO: check if already voted, and if so, undo vote

    db.session.execute(
        db.update(PostComment)
            .where(
                PostComment.post_id == post_id,
                PostComment.id == comment_id,
            ).values(score=PostComment.score + vote.value)
    )
    db.session.commit()
