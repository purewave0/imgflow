function createPostCard(imageUrl, title, upvotes, comments, views) {
    const post = document.createElement('a');
    post.className = 'post';

    const image = document.createElement('img');
    image.src = imageUrl;

    const postInfo = document.createElement('div');
    postInfo.className = 'post-info';

    const titleElement = document.createElement('h3');
    titleElement.textContent = title;

    const postStats = document.createElement('div');
    postStats.className = 'post-stats';

    const upvotesContainer = document.createElement('div');
    const upvotesIcon = document.createElement('span');
    upvotesIcon.textContent = '⬆';
    const upvotesValue = document.createElement('span');
    upvotesValue.textContent = upvotes;

    const commentsContainer = document.createElement('div');
    const commentsIcon = document.createElement('span');
    commentsIcon.textContent = '💬';
    const commentsValue = document.createElement('span');
    commentsValue.textContent = comments;

    const viewsContainer = document.createElement('div');
    const viewsIcon = document.createElement('span');
    viewsIcon.textContent = '👁️';
    const viewsValue = document.createElement('span');
    viewsValue.textContent = views;

    post.append(image, postInfo);
    postInfo.append(titleElement, postStats);
    postStats.append(upvotesContainer, commentsContainer, viewsContainer);

    upvotesContainer.append(upvotesIcon, upvotesValue);
    commentsContainer.append(commentsIcon, commentsValue);
    viewsContainer.append(viewsIcon, viewsValue);

    return post;
}
