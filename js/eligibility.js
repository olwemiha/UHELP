document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('eligibility-form');
    const select = document.getElementById('eligibility-programme');
    const scoreInput = document.getElementById('eligibility-score');
    const scoreType = document.getElementById('eligibility-score-type');
    const result = document.getElementById('eligibility-result');

    if (!(form instanceof HTMLFormElement)
        || !(select instanceof HTMLSelectElement)
        || !(scoreInput instanceof HTMLInputElement)
        || !(scoreType instanceof HTMLElement)
        || !(result instanceof HTMLElement)) return;

    const programmes = new Map();
    try {
        const response = await fetch('/api/programmes');
        const data = await response.json();
        if (!response.ok || !Array.isArray(data)) {
            throw new Error('The programmes list could not be loaded.');
        }

        select.replaceChildren(new Option('Select a programme', ''));
        data.forEach((programme) => {
            programmes.set(programme.id, programme);
            const label = `${programme.institution} — ${programme.programme}`;
            select.add(new Option(label, String(programme.id)));
        });
    } catch (error) {
        console.error('Could not load eligibility programmes:', error);
        select.replaceChildren(new Option('Programmes could not be loaded', ''));
        result.textContent = error instanceof Error
            ? error.message
            : 'Could not connect to the UHELP server.';
        return;
    }

    select.addEventListener('change', () => {
        const programme = programmes.get(Number(select.value));
        if (!programme) {
            scoreType.textContent = '';
            return;
        }
        if (programme.score_type === 'APS' || programme.score_type === 'FPS') {
            scoreType.textContent = `${programme.score_type} minimum listed: ${programme.aps_score ?? 'not listed'}`;
            scoreInput.max = String(programme.max_score || 1000);
        } else {
            scoreType.textContent = 'This programme does not have a comparable APS/FPS score.';
            scoreInput.removeAttribute('max');
        }
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const programme = programmes.get(Number(select.value));
        if (!programme) {
            result.textContent = 'Select a programme first.';
            return;
        }
        result.textContent = 'Checking score...';

        try {
            const response = await fetch('/api/tools/eligibility', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    programme_id: programme.id,
                    score: Number(scoreInput.value),
                    score_type: programme.score_type === 'APS' || programme.score_type === 'FPS'
                        ? programme.score_type
                        : 'APS',
                }),
            });
            const data = await response.json();
            if (!response.ok) {
                const detail = Array.isArray(data.detail)
                    ? data.detail.map((item) => item.msg).join(' ')
                    : data.detail;
                throw new Error(detail || 'Eligibility could not be checked.');
            }
            result.textContent = data.comparable
                ? `${data.message} Required ${data.required_score_type}: ${data.required_score}; your score: ${data.your_score}.`
                : `${data.message} Requirements: ${data.entry_requirement || 'See the institution prospectus.'}`;
        } catch (error) {
            console.error('Eligibility check failed:', error);
            result.textContent = error instanceof Error
                ? error.message
                : 'Could not connect to the UHELP server.';
        }
    });
});
