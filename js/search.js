document.addEventListener('DOMContentLoaded', async () => {
    const searchInput = document.getElementById('programme-query');
    const programmeList = document.getElementById('programme-list');
    const searchStatus = document.getElementById('programme-search-status');

    if (!(searchInput instanceof HTMLInputElement)
        || !(programmeList instanceof HTMLElement)
        || !(searchStatus instanceof HTMLElement)) {
        return;
    }

    let allProgrammes = [];
    const params = new URLSearchParams(window.location.search);
    searchInput.value = params.get('q') || '';

    const renderCards = (programmes) => {
        programmeList.replaceChildren();

        if (programmes.length === 0) {
            searchStatus.textContent = 'No programmes found.';
            return;
        }

        searchStatus.textContent = `Showing ${programmes.length} programme(s).`;

        programmes.forEach((programme) => {
            const card = document.createElement('article');
            card.className = 'programme-card';

            const cardTop = document.createElement('div');
            cardTop.className = 'card-top';

            const institution = document.createElement('span');
            institution.className = 'card-type';
            institution.textContent = programme.institution || 'Institution';

            const title = document.createElement('h3');
            title.className = 'card-title';
            title.textContent = programme.programme || 'Programme';

            const aps = document.createElement('div');
            aps.className = 'card-inst';
            aps.textContent = Number.isFinite(programme.aps_score)
                ? `${programme.score_type || 'Points'} Required: ${programme.aps_score}`
                : programme.score_type === 'Not applicable'
                    ? 'No APS required'
                    : `${programme.score_type || 'APS/FPS'} score not listed`;

            cardTop.append(institution, title, aps);

            const cardBottom = document.createElement('div');
            cardBottom.className = 'card-bottom';

            const requirements = document.createElement('p');
            requirements.className = 'card-desc';
            const label = document.createElement('strong');
            label.textContent = 'Requirements: ';
            requirements.append(
                label,
                document.createTextNode(programme.entry_requirement || 'Check the institution’s current prospectus for admission requirements.')
            );

            const link = document.createElement('a');
            link.className = 'card-link';
            link.href = 'services/eligibility.html';
            link.textContent = 'Check Eligibility →';

            const saveButton = document.createElement('button');
            saveButton.type = 'button';
            saveButton.className = 'save-programme';
            saveButton.textContent = 'Save Programme';
            saveButton.addEventListener('click', async () => {
                saveButton.disabled = true;
                try {
                    const response = await window.uhelpFetch(`/api/saved-programmes/${programme.id}`, {
                        method: 'POST',
                    });
                    const data = await response.json();
                    if (response.status === 401) {
                        window.location.assign('/auth/login.html');
                        return;
                    }
                    if (!response.ok) throw new Error(data.detail || 'Could not save this programme.');
                    saveButton.textContent = 'Saved';
                } catch (error) {
                    console.error('Could not save programme:', error);
                    searchStatus.textContent = error instanceof Error
                        ? error.message
                        : 'Could not connect to the UHELP server.';
                    saveButton.disabled = false;
                }
            });

            cardBottom.append(requirements, link, saveButton);
            card.append(cardTop, cardBottom);
            programmeList.append(card);
        });
    };

    const updateResults = () => {
        const query = searchInput.value.trim().toLocaleLowerCase();
        const filteredProgrammes = allProgrammes.filter((programme) => [
            programme.programme,
            programme.institution,
            programme.entry_requirement,
            programme.faculty,
            programme.department,
            programme.notes,
        ].some((value) => typeof value === 'string' && value.toLocaleLowerCase().includes(query)));

        renderCards(filteredProgrammes);
    };

    searchInput.addEventListener('input', updateResults);
    searchInput.form?.addEventListener('submit', (event) => {
        event.preventDefault();
        const query = searchInput.value.trim();
        const nextUrl = new URL(window.location.href);
        if (query) {
            nextUrl.searchParams.set('q', query);
        } else {
            nextUrl.searchParams.delete('q');
        }
        window.history.replaceState({}, '', nextUrl);
        updateResults();
    });

    programmeList.innerHTML = '';
    searchStatus.textContent = 'Loading programmes...';

    try {
        const response = await window.uhelpFetch('/api/programmes');
        if (!response.ok) {
            throw new Error(`Programme request failed (${response.status}).`);
        }

        const programmes = await response.json();
        if (!Array.isArray(programmes)) {
            throw new Error('The programmes API returned an invalid response.');
        }

        allProgrammes = programmes;
        updateResults();
    } catch (error) {
        console.error('Could not load programmes:', error);
        programmeList.replaceChildren();
        searchStatus.textContent = 'Could not load programmes. Please check that the UHELP server is running and try again.';
    }
});