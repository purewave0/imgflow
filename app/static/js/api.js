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
};
