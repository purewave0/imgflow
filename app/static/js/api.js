const Api = {
    Preferences: {
        _COMMENT_SORTING_KEY: 'comment-sorting',

        getCommentSorting() {
            return localStorage.getItem(this._COMMENT_SORTING_KEY);
        },

        setCommentSorting(sorting) {
            return localStorage.setItem(this._COMMENT_SORTING_KEY, sorting);
        },

        _POST_SORTING_KEY: 'post-sorting',

        getPostSorting() {
            return localStorage.getItem(this._POST_SORTING_KEY);
        },

        setPostSorting(sorting) {
            return localStorage.setItem(this._POST_SORTING_KEY, sorting);
        },
    },


    // -- flows --

    fetchFlowsOverview() {
        return fetch(`/api/flows?overview=1`);
    },

    fetchFlowSuggestions(partialFlowName) {
        return fetch(`/api/flow-suggestions?name=${partialFlowName}`);
    },


    // -- posts --

    fetchPublicPostsByPage(page, sorting) {
        return fetch(`/api/posts?page=${page}&sort=${sorting}`);
    },

    searchPublicPostsByPage(title, page, sorting) {
        return fetch(
            '/api/posts'
            + `?title=${encodeURIComponent(title)}`
            + `&page=${page}`
            + `&sort=${sorting}`
        );
    },

    fetchPost(postId) {
        return fetch(`/api/posts/${postId}`);
    },

    fetchPostCommentsByPage(postId, page, sorting) {
        return fetch(`/api/posts/${postId}/comments?page=${page}&sort=${sorting}`);
    },

    createPost(title, files, isPublic, flows) {
        const formData = new FormData()
        formData.append('title', title);
        formData.append('is_public', isPublic);
        for (const flow of flows) {
            formData.append('flow', flow)
        }

        for (const file of files) {
            // TODO: description
            formData.append('media_file', file.media_file);
            formData.append('description', file.description);
        }

        return fetch('/api/posts', {
            method: 'POST',
            body: formData
        });
    },

    upvotePost(postId) {
        return fetch(`/api/posts/${postId}/votes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'vote': 'upvote'
            }),
        });
    },

    downvotePost(postId) {
        return fetch(`/api/posts/${postId}/votes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'vote': 'downvote'
            }),
        });
    },

    commentOnPost(postId, content) {
        return fetch(`/api/posts/${postId}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'content': content,
            }),
        });
    },

    upvoteComment(postId, commentId) {
        return fetch(`/api/posts/${postId}/comments/${commentId}/votes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'vote': 'upvote'
            }),
        });
    },

    downvoteComment(postId, commentId) {
        return fetch(`/api/posts/${postId}/comments/${commentId}/votes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'vote': 'downvote'
            }),
        });
    },

    replyToComment(postId, commentId, content) {
        return fetch(`/api/posts/${postId}/comments/${commentId}/replies`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'content': content,
            }),
        });
    },

    fetchCommentReplies(postId, commentId, sorting) {
        return fetch(`/api/posts/${postId}/comments/${commentId}/replies?sort=${sorting}`);
    },


    // -- flows & posts --

    fetchPublicPostsInFlowByPage(flowName, page, sorting) {
        return fetch(`/api/flows/${flowName}/posts?page=${page}&sort=${sorting}`);
    }
};
