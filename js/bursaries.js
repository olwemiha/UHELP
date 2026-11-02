document.addEventListener('DOMContentLoaded', async () => {
    const grid = document.getElementById('bursary-list');
    if (!(grid instanceof HTMLElement)) return;

    try {
        const response = await window.uhelpFetch('/api/bursaries');
        if (!response.ok) {
            throw new Error(`Bursary request failed (${response.status}).`);
        }
        const bursaries = await response.json();
        if (!Array.isArray(bursaries)) {
            throw new Error('The bursaries API returned an invalid response.');
        }

        grid.replaceChildren();
        if (bursaries.length === 0) {
            const message = document.createElement('p');
            message.className = 'data-message';
            message.textContent = 'No bursaries are currently available.';
            grid.append(message);
            return;
        }

        bursaries.forEach(b => {
            const card = document.createElement('article');
            card.className = 'programme-card';
            const top = document.createElement('div');
            top.className = 'card-top';
            const provider = document.createElement('span');
            provider.className = 'card-type';
            provider.textContent = b.provider || 'Bursary';
            const name = document.createElement('h3');
            name.className = 'card-title';
            name.textContent = b.name || 'Unnamed bursary';
            const closing = document.createElement('div');
            closing.className = 'card-inst';
            const date = b.closing_date ? new Date(`${b.closing_date}T00:00:00`) : null;
            closing.textContent = date && !Number.isNaN(date.getTime())
                ? `Closing: ${date.toLocaleDateString('en-ZA', { day: 'numeric', month: 'short', year: 'numeric' })}`
                : 'Closing date not provided';
            top.append(provider, name, closing);

            const bottom = document.createElement('div');
            bottom.className = 'card-bottom';
            const description = document.createElement('p');
            description.className = 'card-desc';
            description.textContent = b.description || '';
            bottom.append(description);

            if (typeof b.website === 'string' && /^https?:\/\//i.test(b.website)) {
                const link = document.createElement('a');
                link.className = 'card-link';
                link.href = b.website;
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                link.textContent = 'Visit Website →';
                bottom.append(link);
            }

            card.append(top, bottom);
            grid.append(card);
        });

    } catch (error) {
        console.error('Could not load bursaries:', error);
        const message = document.createElement('p');
        message.className = 'data-message';
        message.textContent = 'Bursaries could not be loaded. Please check that the UHELP server is running and try again.';
        grid.replaceChildren(message);
    }
});