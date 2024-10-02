document.addEventListener('DOMContentLoaded', () => {
    const DateTime = luxon.DateTime;
    const postCreationDate = document.getElementById('post-created-on');
    const postCreatedOn = DateTime
        .fromISO(postCreationDate.textContent.trim());

    postCreationDate.textContent = postCreatedOn.toRelative();
    postCreationDate.title = postCreatedOn
        .toLocaleString(DateTime.DATE_MED_WITH_WEEKDAY)
});
