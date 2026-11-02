document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('contact-form');
    const status = document.getElementById('contact-status');
    if (!(form instanceof HTMLFormElement) || !(status instanceof HTMLElement)) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const button = form.querySelector('button[type="submit"]');
        if (button) button.disabled = true;
        status.textContent = 'Sending your message...';

        try {
            const values = new FormData(form);
            const response = await window.uhelpFetch('/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: values.get('name'),
                    email: values.get('email'),
                    message: values.get('message'),
                }),
            });
            const result = await response.json();
            if (!response.ok) {
                const detail = Array.isArray(result.detail)
                    ? result.detail.map((item) => item.msg).join(' ')
                    : result.detail;
                throw new Error(detail || 'Your message could not be sent.');
            }
            status.textContent = result.message;
            form.reset();
        } catch (error) {
            console.error('Contact submission failed:', error);
            status.textContent = error instanceof Error
                ? error.message
                : 'Could not connect to the UHELP server.';
        } finally {
            if (button) button.disabled = false;
        }
    });
});
