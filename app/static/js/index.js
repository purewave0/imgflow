function createPostCard(
    postId, thumbnailUrl, title, upvotes, commentCount, views
) {
    const post = document.createElement('a');
    post.className = 'post';
    post.href = `/posts/${postId}`;

    const thumbnail = document.createElement('img');
    thumbnail.src = thumbnailUrl;

    const postInfo = document.createElement('div');
    postInfo.className = 'post-info';

    const titleElement = document.createElement('h3');
    titleElement.textContent = title;
    titleElement.title = title;

    const postStats = document.createElement('div');
    postStats.className = 'post-stats';

    const upvotesContainer = document.createElement('div');
    upvotesContainer.className = 'post-stat';
    upvotesContainer.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M320-120v-320H120l360-440 360 440H640v320H320Z"/></svg>';
    const upvotesValue = document.createElement('span');
    upvotesValue.textContent = upvotes;

    const commentsContainer = document.createElement('div');
    commentsContainer.className = 'post-stat';
    commentsContainer.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M240-400h480v-80H240v80Zm0-120h480v-80H240v80Zm0-120h480v-80H240v80Zm-80 400q-33 0-56.5-23.5T80-320v-480q0-33 23.5-56.5T160-880h640q33 0 56.5 23.5T880-800v720L720-240H160Z"/></svg>';
    const commentsValue = document.createElement('span');
    commentsValue.textContent = commentCount;

    const viewsContainer = document.createElement('div');
    viewsContainer.className = 'post-stat';
    viewsContainer.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M480-320q75 0 127.5-52.5T660-500q0-75-52.5-127.5T480-680q-75 0-127.5 52.5T300-500q0 75 52.5 127.5T480-320Zm0-72q-45 0-76.5-31.5T372-500q0-45 31.5-76.5T480-608q45 0 76.5 31.5T588-500q0 45-31.5 76.5T480-392Zm0 192q-146 0-266-81.5T40-500q54-137 174-218.5T480-800q146 0 266 81.5T920-500q-54 137-174 218.5T480-200Z"/></svg>';
    const viewsValue = document.createElement('span');
    viewsValue.textContent = views;

    post.append(thumbnail, postInfo);
    postInfo.append(titleElement, postStats);
    postStats.append(upvotesContainer, commentsContainer, viewsContainer);

    upvotesContainer.append(upvotesValue);
    commentsContainer.append(commentsValue);
    viewsContainer.append(viewsValue);

    return post;
}


document.addEventListener('DOMContentLoaded', () => {
    const gallery = document.getElementById('gallery');

    Api.fetchPublicPosts().then(async (response) => {
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
