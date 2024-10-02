document.addEventListener('DOMContentLoaded', () => {
    const postCreationDate = document.getElementById('post-created-on');
    postCreationDate.textContent = new Date(postCreationDate.textContent).toLocaleString();
});
