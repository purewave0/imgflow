document.addEventListener('DOMContentLoaded', () => {
    // Post
    const DateTime = luxon.DateTime;
    const postCreationDate = document.getElementById('post-created-on');
    const postCreatedOn = DateTime
        .fromISO(postCreationDate.textContent.trim());

    postCreationDate.textContent = postCreatedOn.toRelative();
    postCreationDate.title = postCreatedOn
        .toLocaleString(DateTime.DATETIME_MED_WITH_WEEKDAY)

    const postScore = document.getElementById('post-score');

    const upvotePostButton = document.getElementById('upvote-post');
    if (currentUser.isLoggedIn) {
        upvotePostButton.addEventListener('click', () => {
            const hasUpvotedPost =
                upvotePostButton.classList.contains('upvoted');
            if (hasUpvotedPost) {
                Api.removeUpvoteFromPost(currentPost.post_id);
                postScore.textContent = Number(postScore.textContent) - 1;
            } else {
                Api.upvotePost(currentPost.post_id);
                postScore.textContent = Number(postScore.textContent) + 1;
            }
            upvotePostButton.classList.toggle('upvoted');
        });
    } else {
        upvotePostButton.addEventListener('click', () => {
            // TODO: proper tooltip or redirection
            alert('You must be logged in to upvote this post.');
        });
    }

    // Sorting
    let preferredSorting = Api.Preferences.getCommentSorting();
    if (preferredSorting === null) {
        preferredSorting = 'newest';
        Api.Preferences.setCommentSorting(preferredSorting);
    }

    let currentlySelectedSorting = null;
    const sortingOptions = document.getElementById('comments-sorting').children;
    for (const option of sortingOptions) {
        if (option.dataset.sort === preferredSorting) {
            option.classList.add('selected');
            currentlySelectedSorting = option;
        }

        option.addEventListener('click', () => {
            if (option.classList.contains('selected')) {
                return;
            }

            currentlySelectedSorting.classList.remove('selected');
            option.classList.add('selected');
            currentlySelectedSorting = option;
            Api.Preferences.setCommentSorting(option.dataset.sort);

            // need to reload it all
            commentsDestination.innerHTML = '';
            delete commentsDestination.dataset.allCommentsFetched;
            fetchAndAddComments(0, option.dataset.sort)
        });
    }

    if (currentPost.comment_count === 0) {
        document.body.classList.add('no-comments');
    }


    const markdownRenderer = new marked.Renderer();
    // don't interpret images
    markdownRenderer.image = function (text) {
        return text.raw;
    };

    function parsePurifyMarkdown(content) {
        return DOMPurify.sanitize(
            marked.parse(
                // remove the most common zerowidth characters from the beginning
                content.replace(/^[\u200B\u200C\u200D\u200E\u200F\uFEFF]/,''),
                { renderer: markdownRenderer }
            )
        );
    }

    // Media items descriptions
    const descriptions = document.querySelectorAll('figcaption')
    for (const description of descriptions) {
        description.innerHTML = parsePurifyMarkdown(description.innerHTML);
    }

    // Comments
    let replyForm = null;
    function createComment(
        commentId,
        avatarUrl,
        commenterUsername,
        isoDatetime,
        content,
        score,
        repliesCount,
        hasUpvote,
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
        commentWrapper.dataset.commentId = commentId;

        const commentElement = commentWrapper.querySelector('.comment');

        const avatarElement = commentWrapper.querySelector('.commenter-avatar');
        avatarElement.src = avatarUrl;

        const usernameElement = commentWrapper.querySelector('.commenter-username');
        usernameElement.textContent = commenterUsername;

        commentWrapper.dataset.createdOn = isoDatetime;
        const datetimeElement = commentWrapper.querySelector('.comment-datetime');
        const datetime = DateTime.fromISO(isoDatetime);
        datetimeElement.textContent = datetime.toRelative();
        datetimeElement.title = datetime
            .toLocaleString(DateTime.DATETIME_MED_WITH_WEEKDAY);

        const contentElement = commentWrapper.querySelector('.comment-content');
        contentElement.innerHTML = parsePurifyMarkdown(content)

        //const contentParagraph = document.createElement('p');
        //contentParagraph.textContent = content;
        //contentElement.append(contentParagraph);

        const scoreElement = commentWrapper.querySelector('.comment-score');
        scoreElement.textContent = score;

        const upvoteButton = commentWrapper.querySelector('.action-upvote');
        if (currentUser.isLoggedIn) {
            if (hasUpvote) {
                upvoteButton.classList.add('upvoted');
            }
            upvoteButton.addEventListener('click', () => {
                const hasUpvotedComment =
                    upvoteButton.classList.contains('upvoted');
                if (hasUpvotedComment) {
                    Api.removeUpvoteFromComment(currentPost.post_id, commentId);
                    scoreElement.textContent =
                        Number(scoreElement.textContent) - 1;
                } else {
                    Api.upvoteComment(currentPost.post_id, commentId);
                    scoreElement.textContent =
                        Number(scoreElement.textContent) + 1;
                }
                upvoteButton.classList.toggle('upvoted')
            });
        } else {
            upvoteButton.addEventListener('click', () => {
                // TODO: proper tooltip or redirection
                alert('You must be logged in to upvote this comment.');
            });
        }

        function createShowRepliesButton() {
            const showReplies = document.createElement('div');
            showReplies.className = 'show-replies';
            showReplies.innerHTML = `
                <span class="show-replies-verb verb-show">Show</span>
                <span class="show-replies-verb verb-hide">Hide</span>
                <span class="show-replies-count">${repliesCount}</span>
                <span>replies</span>
            `;
            const showRepliesVerb =
                showReplies.querySelector('.show-replies-verb');

            showReplies.addEventListener('click', async () => {
                const shouldFetchReplies = !(
                    'hasFetchedReplies' in commentWrapper.dataset
                );
                if (!shouldFetchReplies) {
                    if (commentWrapper.classList.contains('showing-replies')) {
                        commentWrapper.classList.remove('showing-replies');
                    } else {
                        commentWrapper.classList.add('showing-replies');
                    }
                    return;
                }

                const repliesCountElement =
                    showReplies.querySelector('.show-replies-count');
                updateCommentReplies(
                    currentPost.post_id,
                    commentId,
                    commentReplies,
                    repliesCountElement
                );

                commentWrapper.dataset.hasFetchedReplies = true;

                if (!commentWrapper.classList.contains('showing-replies')) {
                    commentWrapper.classList.add('showing-replies');
                } else {
                    commentWrapper.classList.remove('showing-replies');
                }
            });

            return showReplies;
        }

        if (repliesCount > 0) {
            const showReplies = createShowRepliesButton(repliesCount);
            commentElement.append(showReplies);
        }

        async function updateCommentReplies(
            postId, commentId, commentRepliesElement, repliesCountElement
        ) {
            const response = await Api.fetchCommentReplies(
                currentPost.post_id, commentId, Api.Preferences.getCommentSorting()
            );
            const replies = await response.json();

            repliesCountElement.textContent = replies.length;

            // TODO: take into account creation date too, for edited comments
            const currentRepliesIds = [];

            for (const replyWrapper of commentRepliesElement.children) {
                currentRepliesIds.push(replyWrapper.dataset.commentId);

                // update relative time
                const createdOn = replyWrapper.dataset.createdOn;
                const datetime = DateTime.fromISO(createdOn);
                const datetimeElement =
                    replyWrapper.querySelector('.comment-datetime');
                datetimeElement.textContent = datetime.toRelative();
                datetimeElement.title = datetime
                    .toLocaleString(DateTime.DATETIME_MED_WITH_WEEKDAY);
            }


            for (const reply of replies) {
                if (currentRepliesIds.includes(String(reply.id))) {
                    // this reply is already present
                    continue;
                }

                const replyElement = createComment(
                    reply.id,
                    '/static/img/cat.png',
                    reply.username,
                    reply.created_on,
                    reply.content,
                    reply.score,
                    reply.reply_count,
                    reply.has_upvote,
                );

                commentRepliesElement.append(replyElement);
            }
        }

        const commentReplies = commentWrapper.querySelector('.comment-replies');

        const replyButton = commentWrapper.querySelector('.action-reply');
        if (!currentUser.isLoggedIn) {
            replyButton.addEventListener('click', () => {
                // TODO: proper tooltip or redirection
                alert('You must be logged in to reply to this comment.');
            });
        } else {
            replyButton.addEventListener('click', () => {
                if (replyForm) {
                    const isReplyingToThisComment =
                        replyForm.dataset.replyingTo === String(commentId);

                    if (isReplyingToThisComment) {
                        replyForm.elements[0].focus();
                        return;
                    }

                    replyForm.remove();
                }

                replyForm = document.createElement('form');
                replyForm.id = 'reply-form';
                replyForm.className = 'comment-form';
                replyForm.dataset.replyingTo = commentId;
                replyForm.innerHTML = `
                    <textarea id="reply-input" class="comment-input" rows="6" maxlength="2000" placeholder="Text a reply…"></textarea>

                    <div id="reply-footer">
                        <button id="reply-cancel" class="cancel-comment" type="button">
                            Cancel
                        </button>

                        <button id="reply-submit" class="submit-comment" type="submit">
                            Reply
                        </button>
                    </div>
                `;

                const replyInput = replyForm.querySelector('#reply-input');
                replyInput.addEventListener('input', () => {
                    if (!replyInput.value.trim()) {
                        replyInput.setCustomValidity('Reply should not be empty.');
                        replyInput.reportValidity();
                    } else {
                        replyInput.setCustomValidity('');
                    }
                });
                const replyCancel = replyForm.querySelector('#reply-cancel');
                replyCancel.addEventListener('click', () => {
                    replyForm.remove();
                    replyForm = null;
                });

                replyForm.addEventListener('submit', async (event) => {
                    event.preventDefault();
                    const response = await Api.replyToComment(
                        currentPost.post_id,
                        commentId,
                        replyInput.value.trim()
                    );

                    commentsCountValue.textContent =
                        Number(commentsCountValue.textContent) + 1;

                    let showRepliesButton =
                        commentWrapper.querySelector('.show-replies');

                    replyForm.remove();
                    replyForm = null;

                    delete commentWrapper.dataset.hasFetchedReplies;

                    if (!showRepliesButton) {
                        // now there *is* a reply. need to add the button
                        showRepliesButton = createShowRepliesButton();
                        commentElement.append(showRepliesButton);
                        showRepliesButton.click();
                    } else {
                        const isShowingReplies =
                            commentWrapper.classList.contains('showing-replies');
                        if (!isShowingReplies) {
                            showRepliesButton.click();
                        } else {
                            // showing current replies, so hide and show them again
                            // to trigger a re-update
                            showRepliesButton.click();
                            showRepliesButton.click();
                        }
                    }
                });

                const showRepliesButton =
                    commentElement.querySelector('.show-replies');
                if (showRepliesButton) {
                    showRepliesButton.before(replyForm);
                } else {
                    commentElement.append(replyForm);
                }

                replyInput.focus();
            });
        }

        return commentWrapper;
    }

    const commentsDestination = document.getElementById('comments');

    function addComments(comments) {
        const fragment = new DocumentFragment();

        for (const comment of comments) {
            const commentElement = createComment(
                comment.id,
                '/static/img/cat.png',
                comment.username,
                comment.created_on,
                comment.content,
                comment.score,
                comment.reply_count,
                comment.has_upvote,
            );
            fragment.append(commentElement);
        }

        commentsDestination.append(fragment);
    }


    const COMMENTS_PER_PAGE = 30;

    function fetchNextPage() {
        const nextPage = Number(commentsDestination.dataset.currentPage) + 1;
        fetchAndAddComments(nextPage, Api.Preferences.getCommentSorting());
    }

    const viewMoreButton = document.getElementById('comments-view-more');
    viewMoreButton.addEventListener('click', fetchNextPage);

    function fetchAndAddComments(page, sorting) {
        commentsDestination.classList.add('loading');
        // TODO: actual loading indicators
        Api.fetchPostCommentsByPage(
            currentPost.post_id,
            page,
            Api.Preferences.getCommentSorting()
        ).then(
            (response) => response.json()
        ).then((comments) => {
            commentsDestination.dataset.currentPage = page;
            addComments(comments);

            const isFullPage = comments.length >= COMMENTS_PER_PAGE;
            if (!isFullPage) {
                // no more comments to fetch
                commentsDestination.dataset.allCommentsFetched = true;
            }
            commentsDestination.classList.remove('loading');
        });
    }

    const commentForm = document.getElementById('comment-form');
    const commentInput = document.getElementById('comment-input');
    const commentsCountValue = document.getElementById('comments-count-value');

    commentInput.addEventListener('input', () => {
        if (!commentInput.value.trim()) {
            commentInput.setCustomValidity('Comment should not be empty.');
            commentInput.reportValidity();
        } else {
            commentInput.setCustomValidity('');
        }
    });

    if (!currentUser.isLoggedIn) {
        commentForm.addEventListener('submit', (event) => {
            event.preventDefault();
            // TODO: proper tooltip or redirection
            alert('You must be logged in to comment on this post.');
        });
    } else {
        commentForm.addEventListener('submit', (event) => {
            event.preventDefault();

            Api.commentOnPost(currentPost.post_id, commentInput.value.trim())
                .then((response) => response.json())
                .then((new_comment) => {
                    const commentElement = createComment(
                        new_comment.id,
                        '/static/img/cat.png',
                        new_comment.username,
                        new_comment.created_on,
                        new_comment.content,
                        new_comment.score,
                        new_comment.reply_count,
                    );
                    commentsDestination.prepend(commentElement);

                    commentsCountValue.textContent =
                        Number(commentsCountValue.textContent) + 1;
                });

            if (document.body.classList.contains('no-comments')) {
                document.body.classList.remove('no-comments');
            }
            commentForm.reset();
        });
    }

    fetchAndAddComments(0, preferredSorting);
});
