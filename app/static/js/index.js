function createPostCard(
    postId, thumbnailUrl, title, upvotes, commentCount, views
) {
    const post = document.createElement('a');
    post.className = 'post';
    post.href = `/post/${postId}`;

    const thumbnail = document.createElement('img');
    thumbnail.src = thumbnailUrl;

    const postInfo = document.createElement('div');
    postInfo.className = 'post-info';

    const titleElement = document.createElement('h3');
    titleElement.textContent = title;

    const postStats = document.createElement('div');
    postStats.className = 'post-stats';

    const upvotesContainer = document.createElement('div');
    const upvotesIcon = document.createElement('span');
    upvotesIcon.className = 'stat-icon'
    upvotesIcon.textContent = '⬆';
    const upvotesValue = document.createElement('span');
    upvotesValue.textContent = upvotes;

    const commentsContainer = document.createElement('div');
    const commentsIcon = document.createElement('span');
    commentsIcon.className = 'stat-icon'
    commentsIcon.textContent = '💬';
    const commentsValue = document.createElement('span');
    commentsValue.textContent = commentCount;

    const viewsContainer = document.createElement('div');
    const viewsIcon = document.createElement('span');
    viewsIcon.className = 'stat-icon'
    viewsIcon.textContent = '👁️';
    const viewsValue = document.createElement('span');
    viewsValue.textContent = views;

    post.append(thumbnail, postInfo);
    postInfo.append(titleElement, postStats);
    postStats.append(upvotesContainer, commentsContainer, viewsContainer);

    upvotesContainer.append(upvotesIcon, upvotesValue);
    commentsContainer.append(commentsIcon, commentsValue);
    viewsContainer.append(viewsIcon, viewsValue);

    return post;
}


document.addEventListener('DOMContentLoaded', () => {
    const gallery = document.getElementById('gallery');

    Api.fetchPosts().then(async (response) => {
        const posts = await response.json();
        for (const post of posts) {
            postCard = createPostCard(
                post.post_id,
                post.thumbnail_url,
                post.title,
                post.score,
                post.comment_count,
                post.views
            );
            gallery.append(postCard);
        }
    });
});
