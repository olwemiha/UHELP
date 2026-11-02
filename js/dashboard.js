document.addEventListener('DOMContentLoaded', async () => {
    const heading = document.getElementById('dashboard-heading');
    const status = document.getElementById('dashboard-status');
    const list = document.getElementById('saved-programmes');
    const userName = document.getElementById('user-name');
    const userEmail = document.getElementById('user-email');
    const userInitial = document.getElementById('user-initial');
    const bursaryList = document.getElementById('dashboard-bursaries');
    if (!(heading instanceof HTMLElement)
        || !(status instanceof HTMLElement)
        || !(list instanceof HTMLElement)
        || !(userName instanceof HTMLElement)
        || !(userEmail instanceof HTMLElement)
        || !(userInitial instanceof HTMLElement)
        || !(bursaryList instanceof HTMLElement)) return;

    try {
        const [profileResponse, savedResponse, bursaryResponse] = await Promise.all([
            window.uhelpFetch('/api/auth/me'),
            window.uhelpFetch('/api/saved-programmes'),
            window.uhelpFetch('/api/bursaries'),
        ]);
        if (profileResponse.status === 401 || savedResponse.status === 401) {
            window.location.assign('/auth/login.html');
            return;
        }
        const profileData = await profileResponse.json();
        const programmes = await savedResponse.json();
        const bursaries = await bursaryResponse.json();
        if (!profileResponse.ok || !savedResponse.ok || !bursaryResponse.ok
            || !Array.isArray(programmes) || !Array.isArray(bursaries)) {
            throw new Error(profileData.detail || 'Could not load your dashboard.');
        }

        const user = profileData.user;
        heading.textContent = `Welcome, ${user.name}`;
        userName.textContent = user.name;
        userEmail.textContent = user.email;
        userInitial.textContent = user.name.trim().charAt(0).toLocaleUpperCase() || 'S';
        list.replaceChildren();
        if (!programmes.length) {
            const empty = document.createElement('p');
            empty.className = 'data-message';
            empty.textContent = 'You have not saved any programmes yet. Browse programmes to add some.';
            list.append(empty);
        } else programmes.forEach((programme) => {
            const card = document.createElement('article');
            card.className = 'programme-card';
            const top = document.createElement('div');
            top.className = 'card-top';
            const institution = document.createElement('span');
            institution.className = 'card-type';
            institution.textContent = programme.institution;
            const name = document.createElement('h3');
            name.className = 'card-title';
            name.textContent = programme.programme;
            const score = document.createElement('div');
            score.className = 'card-inst';
            score.textContent = programme.aps_score === null
                ? 'No APS/FPS score listed'
                : `${programme.score_type || 'Points'} required: ${programme.aps_score}`;
            top.append(institution, name, score);

            const bottom = document.createElement('div');
            bottom.className = 'card-bottom';
            const requirements = document.createElement('p');
            requirements.className = 'card-desc';
            requirements.textContent = programme.entry_requirement || 'Check the institution’s current prospectus for requirements.';
            const remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'save-programme';
            remove.textContent = 'Remove saved programme';
            remove.addEventListener('click', async () => {
                remove.disabled = true;
                try {
                    const response = await window.uhelpFetch(`/api/saved-programmes/${programme.id}`, {
                        method: 'DELETE',
                    });
                    if (!response.ok) throw new Error('Could not remove the saved programme.');
                    card.remove();
                    if (!list.querySelector('.programme-card')) {
                        status.textContent = 'You have not saved any programmes yet.';
                    }
                } catch (error) {
                    console.error('Could not remove saved programme:', error);
                    status.textContent = error instanceof Error
                        ? error.message
                        : 'Could not connect to the UHELP server.';
                    remove.disabled = false;
                }
            });
            bottom.append(requirements, remove);
            card.append(top, bottom);
            list.append(card);
        });
        status.textContent = `Welcome back. You have ${programmes.length} saved programme${programmes.length === 1 ? '' : 's'}.`;

        bursaryList.replaceChildren();
        if (!bursaries.length) {
            const empty = document.createElement('p');
            empty.className = 'data-message';
            empty.textContent = 'No active funding opportunities are listed right now.';
            bursaryList.append(empty);
            return;
        }

        bursaries.slice(0, 3).forEach((bursary) => {
            const item = document.createElement('div');
            item.className = 'dashboard-funding-item';
            const details = document.createElement('div');
            const name = document.createElement('strong');
            name.textContent = bursary.name;
            const provider = document.createElement('span');
            provider.textContent = bursary.provider || 'Funding provider';
            details.append(name, provider);
            item.append(details);

            if (typeof bursary.website === 'string' && /^https?:\/\//i.test(bursary.website)) {
                const link = document.createElement('a');
                link.href = bursary.website;
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                link.textContent = 'Visit provider';
                item.append(link);
            }
            bursaryList.append(item);
        });
    } catch (error) {
        console.error('Could not load dashboard:', error);
        status.textContent = error instanceof Error
            ? error.message
            : 'Could not connect to the UHELP server.';
        const message = document.createElement('p');
        message.className = 'data-message';
        message.textContent = status.textContent;
        list.replaceChildren(message);
    }
});
