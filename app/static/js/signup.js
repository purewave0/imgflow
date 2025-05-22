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

    const loginLink = document.getElementById('login-link');
    loginLink.href += `?redirect_to=${encodeURIComponent(redirectDestinationQuery)}`;

    const usernameInput = document.getElementById('username');
    const usernameAvailabilityMessage = document.getElementById('availability-message');

    const checkUsernameAvailabilityDebounced = debounce(async () => {
        // TODO: loading below the input
        const username = usernameInput.value;
        if (username) {
            const isAvailable = await Api.isUsernameAvailable(username);
            if (isAvailable) {
                usernameInput.setCustomValidity('');
                usernameAvailabilityMessage.dataset.state = 'available';
                usernameAvailabilityMessage.textContent = 'Username available!';
            } else {
                usernameInput.setCustomValidity('Username already taken.');
                usernameAvailabilityMessage.dataset.state = 'taken';
                usernameAvailabilityMessage.textContent = 'Username already taken.';

                // TODO: suggest available variations of the username?
            }
        }
    }, 500);

    usernameInput.addEventListener('input', (event) => {
        usernameInput.setCustomValidity('');
        delete usernameAvailabilityMessage.dataset.state;
        usernameAvailabilityMessage.textContent = '';

        if (
            !usernameInput.value
            || usernameInput.validity.tooShort
            || usernameInput.validity.tooLong
        ) {
            // no need to check availability if it's not even valid
            return;
        }

        checkUsernameAvailabilityDebounced();
    });


    const signupForm = document.getElementById('signup-form');
    signupForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        const response = await Api.signup(username, password);
        if (!response.ok) {
            const result = await response.json();
            switch (result.error) {
                case 'username_already_taken':
                    checkUsernameAvailabilityDebounced();
                    break;
                // TODO: deal with the other possible errors
                default:
                    alert('TODO');
                    break;
            }
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
    });
});
