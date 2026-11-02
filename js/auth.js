document.addEventListener('DOMContentLoaded', () => {
    const status = document.getElementById('auth-status');
    const signupForm = document.getElementById('signup-form');
    const loginForm = document.getElementById('login-form');

    if (!status || (!signupForm && !loginForm)) return;

    const submitAuth = async (form, endpoint, payload) => {
        const button = form.querySelector('button[type="submit"]');
        status.textContent = 'Please wait...';
        if (button) button.disabled = true;

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const result = await response.json();
            if (!response.ok) {
                const detail = Array.isArray(result.detail)
                    ? result.detail.map((item) => item.msg).join(' ')
                    : result.detail;
                throw new Error(detail || 'The request could not be completed.');
            }
            window.location.assign('/dashboard.html');
        } catch (error) {
            console.error('Account request failed:', error);
            status.textContent = error instanceof Error
                ? error.message
                : 'Could not connect to the UHELP server.';
        } finally {
            if (button) button.disabled = false;
        }
    };

    if (signupForm instanceof HTMLFormElement) {
        signupForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const values = new FormData(signupForm);
            submitAuth(signupForm, '/api/auth/register', {
                name: values.get('name'),
                email: values.get('email'),
                password: values.get('password'),
            });
        });
    }

    if (loginForm instanceof HTMLFormElement) {
        loginForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const values = new FormData(loginForm);
            submitAuth(loginForm, '/api/auth/login', {
                email: values.get('email'),
                password: values.get('password'),
            });
        });
    }
});
