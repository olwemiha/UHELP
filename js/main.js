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

    fetch('/api/auth/me')
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
                    const response = await fetch('/api/auth/logout', { method: 'POST' });
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