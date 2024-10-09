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
    }
};
