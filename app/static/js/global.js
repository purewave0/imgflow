// -- header search --

const searchForm = document.getElementById('header-search');
const searchInput = document.getElementById('search');

searchForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const titleQuery = searchInput.value.trim();
    titleQuery.value = titleQuery;

    document.location.href = `/search?title=${encodeURIComponent(titleQuery)}`;
});
