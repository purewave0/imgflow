from enum import Enum

from app.extensions import db
from app.models.post import (
    Post, PostMedia, PostComment, Flow, PostUpvote, CommentUpvote, PostFlow
)
from app.models.user import User


POSTS_PER_PAGE = 20
COMMENTS_PER_PAGE = 30
FLOWS_IN_OVERVIEW = 8
FLOW_SUGGESTIONS_LIMIT = 8


def create_post(title, media_list, is_public, flow_names):
    """Create a post in the database.

    Args:
        title: The title of the post. Must not exceed Post.MAX_NAME_LENGTH
            characters.
        media_list: Collection of dicts containing the media's URL
            ('media_url') and a description ('description') of optional value.
        is_public: If True, the post will show up on public feeds.
        flow_names: Collection of Flows the post will be in. Its length
            must not exceed Post.MAX_FLOWS_PER_POST.

    Returns:
        The newly created Post's columns as a dict; the 'flows' column,
        however, will be 'flow_names' instead, containing the names of the
        Flows this post is in.

    """
    media = []
    for media_item in media_list:
        description = media_item['description']

        media.append(
            PostMedia(
                media_url=media_item['media_url'],
                description=(description if description else None)
            )
        )

    flows = []
    if is_public:
        for flow_name in flow_names:
            flow = _get_flow(flow_name)
            if flow:
                _increment_flow_post_count(flow.id)
            else:
                # new flow: let's create it
                flow = Flow(name=flow_name)
                flow.post_count += 1
                db.session.add(flow)

            flows.append(flow)

    # TODO: check if failed because of post_id collision
    post = Post(title, media, media_list[0]['thumbnail_url'], is_public, flows)

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
        'flow_names':    tuple(flow.name for flow in post.flows),
    }


def comment_on_post(post_id, content):
    """Comment on a post.

    Args:
        post_id: The ID of the post.
        content: The comment's content. Supports Markdown.

    Returns:
        The newly created PostComment's columns as a dict.
    """
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
    """Reply to a comment on a post.

    Args:
        post_id: The ID of the post.
        comment_id: The ID of the comment.
        content: The reply's content. Supports Markdown.

    Returns:
        The newly created PostComment's columns as a dict.
    """
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
    }


def _rows_to_dicts(rows):
    """Convert the given Rows from a SQLAlchemy query into a tuple of dicts."""
    return tuple(row._asdict() for row in rows)


class PostSorting(Enum):
    """Sorting options when fetching posts.

    Attributes:
        NEWEST: Sorts posts by most recently created first.
        TOP: Sorts posts by highest score first.
    """
    NEWEST = 'newest'
    TOP = 'top'


def get_public_posts_by_page(user_id, page, sorting):
    """Return a sorted and paginated collection of Posts as dicts, including upvote
    state.

    Attributes:
        user_id: The current logged in user's ID. If None, upvote states will always be
            False.
        page: The page to fetch.
        sorting: The PostSorting option to use.
    """
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

    if user_id is None:
        statement = statement.add_columns(
            db.literal(False).label('has_upvote')
        )
    else:
        statement = statement.add_columns(
            db.exists().where(
                (PostUpvote.post_id == Post.post_id)
                & (PostUpvote.user_id == user_id)
            ).label('has_upvote')
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


def search_public_posts_by_page(title, page, sorting):
    """Return a sorted and paginated collection of Posts as dicts, filtered by title.

    Attributes:
        title: The title to search for.
        page: The page to fetch.
        sorting: The PostSorting option to use.
    """
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
            Post.is_public == True,
            Post.title.icontains(title)
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
    """Return all of a Post's media as dicts."""
    result = db.session.execute(
        db.select(
            PostMedia.media_url,
            PostMedia.description,
        ).where(PostMedia.post_id == post_id)
    )
    return _rows_to_dicts(result)


def get_post_and_media(post_id, user_id):
    """Return a Post and all of its media (their URL and description) as dicts,
    including whether it was upvoted by the logged in user of the given ID.
    """

    post = db.session.execute(
        db.select(
            Post
        ).options(
            db.selectinload(Post.media)
        ).where(
            Post.post_id == post_id
        )
    ).scalars().one_or_none()

    if not post:
        return None

    has_upvote = False
    if user_id is not None:
        has_upvote = db.session.execute(
            db.select(
                db.exists().where(
                    (PostUpvote.post_id == post_id) &
                    (PostUpvote.user_id == user_id)
                )
            )
        ).scalar()

    media = tuple(
        {
            'media_url': media_item.media_url,
            'description': media_item.description
                if media_item.description else None
        } for media_item in post.media
    )

    flows = tuple(
        {
            'name': flow.name,
            'post_count': flow.post_count
        } for flow in post.flows
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
        'flows': flows,
        'has_upvote': has_upvote,
    }
    return result


class CommentSorting(Enum):
    """Sorting options when fetching comments.

    Attributes:
        NEWEST: Sorts comments by most recently created first.
        MOST-LIKED: Sorts posts by highest score first.
        OLDEST: Sorts comments by most recently created last.
    """
    NEWEST = 'newest'
    MOST_LIKED = 'most-liked'
    OLDEST = 'oldest'


def get_post_comments_by_page(post_id, page, sorting):
    """Return a sorted and paginated collection of a Post's comments as dicts.

    Only top-level comments are included; replies are not.

    Args:
        post_id: The ID of the Post.
        page: The page to fetch.
        sorting: The CommentSorting option to use.
    """
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

    statement = statement.limit(
            COMMENTS_PER_PAGE
        ).offset(
            page*COMMENTS_PER_PAGE
        )

    result = db.session.execute(statement)
    return _rows_to_dicts(result)


def get_post_comments_by_page(post_id, user_id, page, sorting):
    """Return a sorted and paginated collection of a Post's comments as dicts, including
    whether they were upvoted or not.

    Only top-level comments are included; replies are not.

    Args:
        post_id: The ID of the Post.
        page: The page to fetch.
        user_id: The current logged in user's ID. If None, upvote states will always be
            False.
        sorting: The CommentSorting option to use.
    """
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

    if user_id is None:
        statement = statement.add_columns(
            db.literal(False).label('has_upvote')
        )
    else:
        statement = statement.add_columns(
            db.exists().where(
                (CommentUpvote.comment_id == PostComment.id)
                & (CommentUpvote.user_id == user_id)
            ).label('has_upvote')
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

    statement = statement.limit(
            COMMENTS_PER_PAGE
        ).offset(
            page*COMMENTS_PER_PAGE
        )

    result = db.session.execute(statement)
    return _rows_to_dicts(result)


def get_comment_replies(post_id, comment_id, user_id, sorting):
    """Return a sorted collection of a comment's replies as dicts, including upvote
    states.

    Only top-level replies are included; replies to those replies are not.

    Args:
        post_id: The ID of the post.
        comment_id: The ID of the comment.
        user_id: The current logged in user's ID. If None, upvote states will always be
            False.
        sorting: The CommentSorting option to use.
    """
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

    if user_id is None:
        statement = statement.add_columns(
            db.literal(False).label('has_upvote')
        )
    else:
        statement = statement.add_columns(
            db.exists().where(
                (CommentUpvote.comment_id == PostComment.id)
                & (CommentUpvote.user_id == user_id)
            ).label('has_upvote')
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
    """Increase a post's view count by 1."""
    db.session.execute(
        db.update(Post)
            .where(Post.post_id == post_id)
            .values(views=Post.views + 1)
    )
    db.session.commit()


def _increment_post_comment_count(post_id):
    """Increase a post's comment count by 1."""
    db.session.execute(
        db.update(Post)
            .where(Post.post_id == post_id)
            .values(comment_count=Post.comment_count + 1)
    )


def _increment_comment_reply_count(post_id, comment_id):
    """Increase a comment's reply count by 1."""
    db.session.execute(
        db.update(PostComment)
            .where(
                PostComment.id == comment_id,
                PostComment.post_id == post_id,
            ).values(
                reply_count=PostComment.reply_count + 1
            )
    )


def upvote_post(post_id, user_id):
    """Record the user's upvote on a post, if not already upvoted."""

    already_upvoted = db.session.execute(
        db.select(PostUpvote.user_id)
            .where(
                PostUpvote.post_id == post_id,
                PostUpvote.user_id == user_id
            )
    ).mappings().one_or_none() is not None

    if already_upvoted:
        return

    post_upvote = PostUpvote(post_id, user_id)
    db.session.add(post_upvote)

    db.session.execute(
        db.update(Post)
            .where(Post.post_id == post_id)
            .values(score=Post.score + 1)
    )

    db.session.commit()


def remove_upvote_from_post(post_id, user_id):
    """Remove the user's upvote on a post, if upvoted."""

    upvote = db.session.execute(
        db.select(PostUpvote)
            .where(
                PostUpvote.post_id == post_id,
                PostUpvote.user_id == user_id
            )
    ).scalars().one_or_none()

    if not upvote:
        return

    db.session.delete(upvote)

    db.session.execute(
        db.update(Post)
            .where(Post.post_id == post_id)
            .values(score=Post.score - 1)
    )

    db.session.commit()


def upvote_comment(comment_id, user_id):
    """Record the user's upvote on a comment, if not already upvoted."""

    already_upvoted = db.session.execute(
        db.select(CommentUpvote.user_id)
            .where(
                CommentUpvote.comment_id == comment_id,
                CommentUpvote.user_id == user_id
            )
    ).mappings().one_or_none() is not None

    if already_upvoted:
        return

    comment_upvote = CommentUpvote(comment_id, user_id)
    db.session.add(comment_upvote)

    db.session.execute(
        db.update(PostComment)
            .where(
                PostComment.id == comment_id,
            ).values(score=PostComment.score + 1)
    )

    db.session.commit()


def remove_upvote_from_comment(post_id, comment_id, user_id):
    """Remove the user's upvote on a comment, if upvoted."""

    upvote = db.session.execute(
        db.select(CommentUpvote)
            .where(
                CommentUpvote.comment_id == comment_id,
                CommentUpvote.user_id == user_id
            )
    ).scalars().one_or_none()

    if not upvote:
        return

    db.session.delete(upvote)

    db.session.execute(
        db.update(PostComment)
            .where(
                PostComment.id == comment_id,
                PostComment.post_id == post_id,
            ).values(score=PostComment.score - 1)
    )

    db.session.commit()


# -- flows --

def _get_flow(name):
    """Return a Flow object by name."""
    result = db.session.execute(
        db.select(
            Flow
        ).where(
            Flow.name == name
        )
    ).scalar()

    return result


def get_flow(name):
    """Return a Flow as a dict by name."""
    result = db.session.execute(
        db.select(
            Flow.id,
            Flow.name,
            Flow.post_count,
        ).where(
            Flow.name == name
        )
    ).mappings().one_or_none()

    if result is None:
        return None

    return dict(result)


def _increment_flow_post_count(flow_id):
    """Increase a flow's post count by 1."""
    db.session.execute(
        db.update(Flow)
            .where(Flow.id == flow_id)
            .values(post_count=Flow.post_count + 1)
    )


def get_public_posts_in_flow_by_page(flow_id, page, sorting):
    """Return a sorted and paginated collection of posts in a flow as dicts.

    All returned posts are public, as private posts can't be added to flows.
    """
    statement = db.select(
            Post.post_id,
            Post.title,
            Post.thumbnail_url,
            Post.created_on,
            Post.updated_on,
            Post.score,
            Post.comment_count,
            Post.views,
        ).join(
            Post.flows
        ).where(
            Flow.id == flow_id,
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


def thumbnail_by_flow(flow):
    """Return the thumbnail URL of a flow.

    The thumbnail of a flow is the thumbnail of the highest-scored post in that
    flow.
    """
    top_post_thumbnail_from_flow = db.session.execute(
        db.select(
            Post.thumbnail_url
        ).join(
            Post.flows
        ).order_by(
            Post.score.desc(),
            Post.created_on.desc(),
        ).where(
            Flow.id == flow.id
        ).limit(1)
    ).scalar()

    return top_post_thumbnail_from_flow


def get_flows_overview():
    """Return FLOWS_IN_OVERVIEW flows, ordered by highest post count first.

    Returns:
        A collection of dicts, each with the flow's name ('name') and its
        thumbnail ('thumbnail_url'; see thumbnail_by_flow())
    """
    # TODO: expand upon this algorithm
    top_flows = db.session.execute(
        db.select(
            Flow
        ).order_by(
            Flow.post_count.desc(),
            Flow.name.asc(),
        ).limit(FLOWS_IN_OVERVIEW)
    ).scalars().all()

    overview = tuple(
        {
            'name': flow.name,
            'thumbnail_url': thumbnail_by_flow(flow)
        } for flow in top_flows
    )

    return overview


def _escaped_search_text(text):
    """Return `text` with any LIKE special characters (%, _, \) escaped."""
    return text.replace("%", "\\%").replace("\\", "\\\\").replace("_", "\\_")


def suggest_flows_by_name(partial_name):
    result = db.session.execute(
        db.select(
            Flow.name,
            Flow.post_count
        ).where(
            Flow.name.like(
                _escaped_search_text(partial_name) + '%'
            )
        ).order_by(
            Flow.post_count.desc(),
            Flow.name.asc(),
        ).limit(
            FLOW_SUGGESTIONS_LIMIT
        )
    )

    return _rows_to_dicts(result)


# -- users --

def create_user(name, password):
    """Create a user in the database.

    Args:
        name: The username. Must be between User.MIN_NAME_LENGTH and
            User.MAX_NAME_LENGTH characters.
        password: The password. Must be between User.MIN_PASSWORD_LENGTH and
            User.MAX_PASSWORD_LENGTH characters.

    Returns:
        The newly created User object.
    """
    user = User(name, password)

    db.session.add(user)
    db.session.commit()

    return user


def is_username_taken(name):
    """Return whether the given username is already taken."""
    is_taken = db.session.execute(
        db.select(
            User.name
        ).where(
            User.name == name
        )
    ).scalar() is not None

    # TODO: case-insensitive username indexing, because currently it's case-sensitive

    return is_taken


def get_user_by_name(name):
    """Return the User with the given name, or None."""
    user = db.session.execute(
        db.select(
            User
        ).where(
            User.name == name
        )
    ).scalar_one_or_none()

    return user
