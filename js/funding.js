document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('funding-form');
    const input = document.getElementById('funding-query');
    const status = document.getElementById('funding-status');
    const results = document.getElementById('funding-results');
    if (!(form instanceof HTMLFormElement)
        || !(input instanceof HTMLInputElement)
        || !(status instanceof HTMLElement)
        || !(results instanceof HTMLElement)) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const query = input.value.trim();
        status.textContent = 'Searching funding opportunities...';
        results.replaceChildren();

        try {
            const response = await fetch(`/api/funding?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            if (!response.ok || !Array.isArray(data)) {
                const detail = Array.isArray(data.detail)
                    ? data.detail.map((item) => item.msg).join(' ')
                    : data.detail;
                throw new Error(detail || 'Funding opportunities could not be loaded.');
            }

            status.textContent = data.length
                ? `${data.length} funding opportunit${data.length === 1 ? 'y' : 'ies'} found. Check each provider’s current criteria and deadline.`
                : 'No funding opportunities matched your search.';

            data.forEach((item) => {
                const card = document.createElement('article');
                card.className = 'programme-card';
                const top = document.createElement('div');
                top.className = 'card-top';
                const provider = document.createElement('span');
                provider.className = 'card-type';
                provider.textContent = item.provider || 'Funding provider';
                const title = document.createElement('h3');
                title.className = 'card-title';
                title.textContent = item.name;
                const deadline = document.createElement('div');
                deadline.className = 'card-inst';
                deadline.textContent = item.closing_date
                    ? `Closing: ${new Date(`${item.closing_date}T00:00:00`).toLocaleDateString('en-ZA')}`
                    : 'Closing date not listed';
                top.append(provider, title, deadline);

                const bottom = document.createElement('div');
                bottom.className = 'card-bottom';
                const description = document.createElement('p');
                description.className = 'card-desc';
                description.textContent = `${item.field_of_study || 'All study fields'} — ${item.description || ''}`;
                bottom.append(description);
                if (typeof item.website === 'string' && /^https?:\/\//i.test(item.website)) {
                    const link = document.createElement('a');
                    link.className = 'card-link';
                    link.href = item.website;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.textContent = 'Visit provider →';
                    bottom.append(link);
                }
                card.append(top, bottom);
                results.append(card);
            });
        } catch (error) {
            console.error('Funding search failed:', error);
            status.textContent = error instanceof Error
                ? error.message
                : 'Could not connect to the UHELP server.';
        }
    });
});
