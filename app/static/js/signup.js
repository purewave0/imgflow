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

    const signupForm = document.getElementById('signup-form');
    signupForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        const response = await Api.signup(username, password); // TODO

        document.location.href = '/';
        // TODO: receive 'redirect_to' from login page
        /*
        const urlParams = new URLSearchParams(window.location.search);
        const redirectDestinationQuery = urlParams.get('redirect_to');
        if (!redirectDestinationQuery) {
            document.location.href = '/';
            return;
        }

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
        */
    });
});
