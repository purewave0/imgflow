
document.addEventListener('DOMContentLoaded', () => {
    const POSTS_PER_PAGE = 20;

    const createdOn = document.getElementById('created-on');
    createdOn.textContent = new Date(createdOn.textContent).toLocaleDateString();

    let currentlySelectedSorting = document.getElementById('sort-newest');

    const gallery = new Gallery({
        containerId: 'gallery',
        postsPerPage: POSTS_PER_PAGE,
        fetchDataByPage: (page) => {
            return Api.fetchUserPublicPostsByPage(
                thisUser.username, page, currentlySelectedSorting.dataset.sort
            )
        },
    });

    const sortingOptions = document.getElementById('posts-sorting').children;
    for (const option of sortingOptions) {
        option.addEventListener('click', () => {
            if (option.classList.contains('selected')) {
                return;
            }

            currentlySelectedSorting.classList.remove('selected');
            option.classList.add('selected');
            currentlySelectedSorting = option;

            // need to reload it all
            gallery.reloadAll();
        });
    }

    function runOnceAllImagesLoad(images, func) {
        Promise.all(
            images
                .filter(img => !img.complete)
                .map(
                    img => new Promise(resolve => {
                        img.onload = img.onerror = resolve;
                    })
                )
        ).then(func);
    }
});
