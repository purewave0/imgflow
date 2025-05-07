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

    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', (event) => {
        event.preventDefault();

        alert('TODO');

        // TODO: if applicable, return user to where they came from
    });
});
