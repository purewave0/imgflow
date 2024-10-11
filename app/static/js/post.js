document.addEventListener('DOMContentLoaded', () => {
    // Post
    const DateTime = luxon.DateTime;
    const postCreationDate = document.getElementById('post-created-on');
    const postCreatedOn = DateTime
        .fromISO(postCreationDate.textContent.trim());

    postCreationDate.textContent = postCreatedOn.toRelative();
    postCreationDate.title = postCreatedOn
        .toLocaleString(DateTime.DATE_MED_WITH_WEEKDAY)

    // Sorting
    const sortingOptions = document.getElementById('comments-sorting').children;
    let currentlySelectedSort = document.getElementById('sort-newest');
    for (const option of sortingOptions) {
        option.addEventListener('click', () => {
            if (option.classList.contains('selected')) {
                return;
            }

            currentlySelectedSort.classList.remove('selected');
            option.classList.add('selected');
            currentlySelectedSort = option;

            switch (option.id) {
                case 'sort-newest':
                    // TODO
                    break;
                case 'sort-most-liked':
                    // TODO
                    break;
                case 'sort-oldest':
                    // TODO
                    break;
            }
        });
    }

    // Comments
    function createComment(
        avatarUrl, commenterUsername, isoDatetime, content, score
    ) {
        const commentStructure = `
            <div class="comment">
                <div class="comment-info">
                    <img class="commenter-avatar">
                    <span class="commenter-username"></span>
                    <span class="comment-info-separator">·</span>
                    <span class="comment-datetime"></span>
                </div>
                <div class="comment-content"></div>
                <div class="comment-footer">
                    <div class="action-section">
                        <svg class="action-upvote" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M320-120v-320H120l360-440 360 440H640v320H320Z"/></svg>
                        <span class="comment-score"></span>
                        <svg class="action-downvote" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M320-120v-320H120l360-440 360 440H640v320H320Z"/></svg>
                    </div>

                    <div class="action-section action-reply">
                         <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M760-200v-160q0-50-35-85t-85-35H273l144 144-57 56-240-240 240-240 57 56-144 144h367q83 0 141.5 58.5T840-360v160h-80Z"/></svg>
                         <span>Reply</span>
                    </div>
                </div>
            </div>
            <div class="comment-replies"></div>
        `;
        const commentWrapper = document.createElement('div');
        commentWrapper.className = 'comment-wrapper';
        commentWrapper.innerHTML = commentStructure;
        console.log(commentWrapper);

        const avatarElement = commentWrapper.querySelector('.commenter-avatar');
        avatarElement.src = avatarUrl;

        const usernameElement = commentWrapper.querySelector('.commenter-username');
        usernameElement.textContent = commenterUsername;

        const datetimeElement = commentWrapper.querySelector('.comment-datetime');
        const datetime = DateTime.fromISO(isoDatetime);
        datetimeElement.textContent = datetime.toRelative();
        datetimeElement.title = datetime
            .toLocaleString(DateTime.DATE_MED_WITH_WEEKDAY);

        const contentElement = commentWrapper.querySelector('.comment-content');
        // TODO: markdown interpreting
        const contentParagraph = document.createElement('p');
        contentParagraph.textContent = content;
        contentElement.append(contentParagraph);

        const scoreElement = commentWrapper.querySelector('.comment-score');
        scoreElement.textContent = score;

        return commentWrapper;
    }
    const commentsDestination = document.getElementById('comments');

    const sampleComment = createComment(
        '/static/img/cat.png',
        'dynamic_comment',
        '2024-10-11T08:16:00Z',
        'Hello, this is a test.',
        15
    );
    commentsDestination.append(sampleComment);
});
