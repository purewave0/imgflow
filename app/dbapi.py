import random
import string

from app.extensions import db
from app.models.post import Post, PostMedia, PostDescription


_post_id_charset = string.ascii_letters + string.digits # a-z A-Z 0-9

def random_post_id():
    return ''.join(
        random.choices(_post_id_charset, k=Post.POST_ID_LENGTH)
    )
    

def create_post(title, media_list):
    post_id = random_post_id()

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
    post = Post(
        post_id=post_id,
        title=title,
        media=media,
        score=0,
        comments=[],
        views=0,
    )
    db.session.add(post)
    db.session.commit()
    return post
