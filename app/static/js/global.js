function debounce(func, timeout) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(
            () => { func.apply(this, args); },
            timeout
        );
    };
}


// -- header search --

const searchForm = document.getElementById('header-search');
const searchInput = document.getElementById('search');

searchForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const titleQuery = searchInput.value.trim();
    titleQuery.value = titleQuery;

    document.location.href = `/search?title=${encodeURIComponent(titleQuery)}`;
});

const loginButton = document.getElementById('header-login');
if (loginButton) {
    const currentPage = document.location.pathname;
    loginButton.href = `/login?redirect_to=${encodeURIComponent(currentPage)}`;
}
