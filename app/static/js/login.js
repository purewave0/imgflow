document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('password');
    const passwordVisibilityToggle =
        document.getElementById('password-visibility-toggle');

    passwordVisibilityToggle.addEventListener('click', () => {
        passwordInput.type = (passwordInput.type === 'password')
            ? 'text'
            : 'password';
        passwordVisibilityToggle.classList.toggle('visible');
    });

    const urlParams = new URLSearchParams(window.location.search);
    const redirectDestinationQuery = urlParams.get('redirect_to') || '/';

    const signupLink = document.getElementById('signup-link');
    signupLink.href += `?redirect_to=${encodeURIComponent(redirectDestinationQuery)}`;

    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        const response = await Api.login(username, password); // TODO

        const redirectDestination = (
            // ensure we always redirect to a page within imgflow
            document.location.protocol
            + "//"
            + document.location.host
            + decodeURIComponent(redirectDestinationQuery)
        );
        try {
            document.location.href = redirectDestination;
        } catch {
            // malformed 'redirect_to'
            document.location.href = '/';
        }
    });
});
