const Api = {
    Preferences: {
        _SORT_KEY: 'sort',

        getSort() {
            return localStorage.getItem(this._SORT_KEY);
        },

        setSort(sort) {
            return localStorage.setItem(this._SORT_KEY, sort);
        },
    },

    fetchPublicPostsByPage(page) {
        return fetch(`/api/posts?page=${page}`);
    },

    fetchPost(postId) {
        return fetch(`/api/posts/${postId}`);
    },

    fetchPostComments(postId, sorting) {
        return fetch(`/api/posts/${postId}/comments?sort=${sorting}`);
    },

    createPost(title, files, isPublic) {
        const formData = new FormData()
        formData.append('title', title);
        formData.append('is_public', isPublic);
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
};
