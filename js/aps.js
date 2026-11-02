document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('aps-form');
    const result = document.getElementById('aps-result');
    if (!(form instanceof HTMLFormElement) || !(result instanceof HTMLElement)) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        result.textContent = 'Calculating...';
        const values = new FormData(form);
        const subjects = values.getAll('subject').map((subject, index) => ({
            subject: String(subject).trim(),
            mark: Number(values.getAll('mark')[index]),
        }));

        try {
            const response = await fetch('/api/tools/aps', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ subjects }),
            });
            const data = await response.json();
            if (!response.ok) {
                const detail = Array.isArray(data.detail)
                    ? data.detail.map((item) => item.msg).join(' ')
                    : data.detail;
                throw new Error(detail || 'The APS estimate could not be calculated.');
            }

            const heading = document.createElement('h3');
            heading.textContent = `Estimated APS: ${data.aps_score}`;
            const breakdown = document.createElement('p');
            breakdown.textContent = data.subjects_counted
                .map((item) => `${item.subject}: level ${item.points}`)
                .join(' · ');
            const notice = document.createElement('p');
            notice.textContent = data.notice;
            result.replaceChildren(heading, breakdown, notice);
        } catch (error) {
            console.error('APS calculation failed:', error);
            result.textContent = error instanceof Error
                ? error.message
                : 'Could not connect to the UHELP server.';
        }
    });
});