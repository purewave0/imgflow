document.addEventListener('DOMContentLoaded', () => {
    const DateTime = luxon.DateTime;
    const postCreationDate = document.getElementById('post-created-on');
    const postCreatedOn = DateTime
        .fromISO(postCreationDate.textContent.trim());

    postCreationDate.textContent = postCreatedOn.toRelative();
    postCreationDate.title = postCreatedOn
        .toLocaleString(DateTime.DATE_MED_WITH_WEEKDAY)

    const sortingOptions = document.getElementById('comments-sorting').children;
    let currentlySelectedSort = document.getElementById('sort-newest');
    for (const option of sortingOptions) {
        option.addEventListener('click', () => {
            if (option.classList.contains('selected')) {
                return;
            }

            currentlySelectedSort.classList.remove('selected');
            option.classList.add('selected');
            currentlySelectedSort = option;

            switch (option.id) {
                case 'sort-newest':
                    // TODO
                    break;
                case 'sort-most-liked':
                    // TODO
                    break;
                case 'sort-oldest':
                    // TODO
                    break;
            }
        });
    }
});
