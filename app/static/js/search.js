/*
function createFlowCard(flowName, thumbnailUrl) {
    const flow = document.createElement('li');
    flow.className = 'flow-compact';
    flow.href = `/flows/${flowName}`;
    flow.innerHTML = `
        <a class="flow-link">
            <img class="flow-thumbnail">
            <h3 class="flow-name"></h3>
        </a>
    `;

    const flowLink = flow.querySelector('.flow-link');
    flowLink.href = `/flows/${flowName}`;

    const thumbnail = flow.querySelector('.flow-thumbnail');
    thumbnail.src = thumbnailUrl;
    thumbnail.alt = flowName;

    const title = flow.querySelector('.flow-name');
    title.textContent = flowName;

    title.parentElement.title = flowName; // in case the title gets ellipsized

    return flow;
}
*/


document.addEventListener('DOMContentLoaded', () => {

    const POSTS_PER_PAGE = 20;

    // Sorting
    let preferredSorting = Api.Preferences.getPostSorting();
    if (preferredSorting === null) {
        preferredSorting = 'newest';
        Api.Preferences.setPostSorting(preferredSorting);
    }

    const urlParams = new URLSearchParams(window.location.search);
    const titleQuery = urlParams.get('title');

    const searchInput = document.getElementById('search');
    searchInput.value = titleQuery;
    const searchQueryDisplays = document.getElementsByClassName('search-query');
    for (const element of searchQueryDisplays) {
        element.textContent = titleQuery;
        element.title = titleQuery;
    }

    const gallery = new Gallery({
        containerId: 'gallery',
        postsPerPage: POSTS_PER_PAGE,
        fetchDataByPage: (page) => {
            return Api.searchPublicPostsByPage(
                titleQuery, page, Api.Preferences.getPostSorting()
            )
        },
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

    /* -- TODO: add flows later
    const flowsDestination = document.getElementById('flows');
    document.body.dataset.flowsState = 'fetch';
    Api.fetchFlowsOverview()
        .then((response) => response.json())
        .then((overview) => {
            const fragment = new DocumentFragment();
            const thumbnails = [];

            for (const flow of overview) {
                const flowCard = createFlowCard(flow.name, flow.thumbnail_url);
                const thumbnail = flowCard.querySelector('.flow-thumbnail');
                thumbnails.push(thumbnail);

                fragment.append(flowCard);
            }

            flowsDestination.append(fragment);

            runOnceAllImagesLoad(thumbnails, () => {
                document.body.dataset.flowsState = 'all-flows-fetched';
            });
        });
    */
});
