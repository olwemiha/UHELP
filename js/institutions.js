document.addEventListener('DOMContentLoaded', async () => {
    const grid = document.getElementById('institution-list');
    const form = document.getElementById('institution-search');
    const input = document.getElementById('institution-query');
    const status = document.getElementById('institution-search-status');

    if (!(grid instanceof HTMLElement)
        || !(form instanceof HTMLFormElement)
        || !(input instanceof HTMLInputElement)
        || !(status instanceof HTMLElement)) {
        return;
    }

    const params = new URLSearchParams(window.location.search);
    input.value = params.get('q') || '';

    const loadInstitutions = async () => {
        const query = input.value.trim();
        status.textContent = 'Loading institutions...';
        grid.replaceChildren();

        try {
            const url = window.uhelpApiUrl('/api/institutions');
            if (query) url.searchParams.set('q', query);

            const response = await window.uhelpFetch(url);
            if (!response.ok) {
                throw new Error(`Institution request failed (${response.status}).`);
            }

            const institutions = await response.json();
            if (!Array.isArray(institutions)) {
                throw new Error('The institutions API returned an invalid response.');
            }

            institutions.forEach((institution) => {
                const card = document.createElement('article');
                card.className = 'programme-card';

                const top = document.createElement('div');
                top.className = 'card-top';
                const type = document.createElement('span');
                type.className = 'card-type';
                type.textContent = institution.type || 'Institution';
                const name = document.createElement('h3');
                name.className = 'card-title';
                name.textContent = institution.name || 'Unnamed institution';
                const details = document.createElement('div');
                details.className = 'card-inst';
                details.textContent = [institution.province, institution.short_name]
                    .filter(Boolean)
                    .join(' · ');
                top.append(type, name, details);

                const bottom = document.createElement('div');
                bottom.className = 'card-bottom';
                const description = document.createElement('p');
                description.className = 'card-desc';
                description.textContent = `Explore programmes offered at ${institution.short_name || institution.name}.`;
                const link = document.createElement('a');
                link.className = 'card-link';
                const programmeSearch = new URLSearchParams({ q: institution.name });
                link.href = `programmes.html?${programmeSearch.toString()}`;
                link.textContent = 'View Programmes →';
                bottom.append(description, link);

                card.append(top, bottom);
                grid.append(card);
            });

            status.textContent = institutions.length
                ? `${institutions.length} institution${institutions.length === 1 ? '' : 's'} found.`
                : 'No institutions matched your search.';
        } catch (error) {
            console.error('Could not load institutions:', error);
            const message = document.createElement('p');
            message.className = 'data-message';
            message.textContent = 'Institutions could not be loaded. Please check that the UHELP server is running and try again.';
            grid.append(message);
            status.textContent = 'Could not connect to the institutions service.';
        }
    };

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const query = input.value.trim();
        const nextUrl = new URL(window.location.href);
        if (query) {
            nextUrl.searchParams.set('q', query);
        } else {
            nextUrl.searchParams.delete('q');
        }
        window.history.replaceState({}, '', nextUrl);
        loadInstitutions();
    });

    await loadInstitutions();
});