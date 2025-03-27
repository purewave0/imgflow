document.addEventListener('DOMContentLoaded', () => {

    const POSTS_PER_PAGE = 20;

    // Sorting
    let preferredSorting = Api.Preferences.getPostSorting();
    if (preferredSorting === null) {
        preferredSorting = 'newest';
        Api.Preferences.setPostSorting(preferredSorting);
    }

    const gallery = new Gallery({
        containerId: 'gallery',
        postsPerPage: POSTS_PER_PAGE,
        fetchDataByPage: (page) => {
            return Api.fetchPublicPostsInFlowByPage(
                currentFlow.name, page, Api.Preferences.getPostSorting()
            )
        }
    });

    let currentlySelectedSorting = null;
    const sortingOptions = document.getElementById('posts-sorting').children;
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
            Api.Preferences.setPostSorting(option.dataset.sort);

            // need to reload it all
            gallery.reloadAll();
        });
    }
});
