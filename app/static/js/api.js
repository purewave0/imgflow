const Api = {
    fetchPublicPosts() {
        return fetch('/api/posts');
    },

    fetchPost(postId) {
        return fetch(`/api/posts/${postId}`);
    },

    fetchPostComments(postId) {
        return fetch(`/api/posts/${postId}/comments`);
    },

    createPost(title, mediaFiles, isPublic) {
        const formData = new FormData()
        formData.append('title', title);
        formData.append('is_public', isPublic);
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
