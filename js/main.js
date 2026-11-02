(() => {
    const localHosts = new Set(['localhost', '127.0.0.1']);
    const apiOrigin = localHosts.has(window.location.hostname)
        ? window.location.port === '8000'
            ? window.location.origin
            : 'http://127.0.0.1:8000'
        : window.location.hostname === 'uhelp.onrender.com'
            ? window.location.origin
            : 'https://uhelp.onrender.com';

    window.uhelpApiUrl = (path) => new URL(path, apiOrigin);
    window.uhelpFetch = (path, options = {}) => fetch(window.uhelpApiUrl(path), {
        ...options,
        credentials: 'include',
    });
})();

document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menu-toggle');
    const navLinks = document.getElementById('nav-links');

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            menuToggle.textContent = navLinks.classList.contains('active') ? '✕' : '☰';
        });
    }

    const navActions = document.querySelector('.nav-actions');
    const loginLink = navActions?.querySelector('.btn-login');
    const signupLink = navActions?.querySelector('.btn-primary');
    if (!navActions || !loginLink || !signupLink || !/^https?:$/.test(window.location.protocol)) return;

    window.uhelpFetch('/api/auth/me')
        .then(async (response) => {
            if (response.status === 401) return null;
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Could not check account status.');
            return data.user;
        })
        .then((user) => {
            if (!user) return;
            loginLink.hidden = true;
            signupLink.href = '/dashboard.html';
            signupLink.textContent = 'Dashboard';

            const logoutButton = document.createElement('button');
            logoutButton.type = 'button';
            logoutButton.className = 'btn-login';
            logoutButton.textContent = 'Log Out';
            logoutButton.addEventListener('click', async () => {
                logoutButton.disabled = true;
                try {
                    const response = await window.uhelpFetch('/api/auth/logout', { method: 'POST' });
                    if (!response.ok) throw new Error('Could not log out.');
                    window.location.reload();
                } catch (error) {
                    console.error('Logout failed:', error);
                    logoutButton.disabled = false;
                }
            });
            navActions.append(logoutButton);
        })
        .catch((error) => console.error('Could not check account status:', error));
});