const Api = {
    fetchPosts() {
        return fetch('/api/posts');
    },

    fetchPost(postId) {
        return fetch(`/api/posts/${postId}`);
    },

    fetchPostComments(postId) {
        return fetch(`/api/posts/${postId}/comments`);
    },

    createPost(title, mediaFiles) {
        const formData = new FormData()
        formData.append('title', title);
        for (const file of mediaFiles) {
            // TODO: description
            formData.append('file', file);
        }

        return fetch('/api/posts', {
            method: 'POST',
            body: formData
        });
    }
};
