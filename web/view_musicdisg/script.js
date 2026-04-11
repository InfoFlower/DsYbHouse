let allVideos = [];
let allHeader = [];
let currentView = 'grid';

document.addEventListener('DOMContentLoaded', function () {
    loadMusicDiscogs();

    document.getElementById('channel-filter').addEventListener('change', displayFilteredVideos);
    document.getElementById('genre-filter').addEventListener('change', displayFilteredVideos);
    document.getElementById('rating-filter').addEventListener('change', displayFilteredVideos);
    document.getElementById('year-filter').addEventListener('change', displayFilteredVideos);
    document.getElementById('sort-select').addEventListener('change', displayFilteredVideos);
    document.getElementById('reset-btn').addEventListener('click', resetFilters);
    document.getElementById('view-toggle').addEventListener('click', toggleView);
});

/* ---------- helpers ---------- */

function idx(key) {
    return allHeader.indexOf(key);
}

function row(video, key) {
    const i = idx(key);
    return i >= 0 ? video[i] : null;
}

function parseList(raw) {
    if (!raw) return [];
    try {
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [parsed];
    } catch {
        return [raw];
    }
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/* ---------- view toggle ---------- */

function toggleView() {
    const toggleBtn = document.getElementById('view-toggle');
    const iconContainer = toggleBtn.querySelector('.icon-squares') || toggleBtn.querySelector('.icon-lines');

    if (currentView === 'grid') {
        currentView = 'list';
        iconContainer.className = 'icon-lines';
        iconContainer.innerHTML = '<div class="line"></div><div class="line"></div><div class="line"></div>';
    } else {
        currentView = 'grid';
        iconContainer.className = 'icon-squares';
        iconContainer.innerHTML = '<div class="square"></div><div class="square"></div><div class="square"></div><div class="square"></div>';
    }
    displayFilteredVideos();
}

/* ---------- data loading ---------- */

function loadMusicDiscogs() {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<div class="spinner"></div><p>Loading consolidated data…</p>';

    fetch('/api/consolidated_data/send_musicdiscg/')
        .then(r => {
            if (!r.ok) throw new Error('Network response was not ok');
            return r.json();
        })
        .then(data => {
            if (data.status === 'success') {
                allVideos = data.videos;
                allHeader = data.header;
                populateFilters();
                displayFilteredVideos();
            } else {
                resultsDiv.innerHTML = '<p>Error loading data.</p>';
            }
        })
        .catch(err => {
            resultsDiv.innerHTML = '<p>Error: ' + escapeHtml(err.message) + '</p>';
        });
}

/* ---------- filters ---------- */

function collectFilterValues(videos) {
    const channels = new Set();
    const genres = new Set();
    const years = new Set();

    videos.forEach(v => {
        const ch = row(v, 'music_videoOwnerChannelTitle') || row(v, 'music_channelTitle');
        if (ch) channels.add(ch);

        const g = row(v, 'genres');
        parseList(g).forEach(x => { if (x) genres.add(x); });

        const y = row(v, 'year');
        if (y) years.add(y);
    });

    return { channels, genres, years };
}

function fillSelect(selectEl, values) {
    while (selectEl.options.length > 1) selectEl.remove(1);
    [...values].sort().forEach(val => {
        const opt = document.createElement('option');
        opt.value = val;
        opt.textContent = val;
        selectEl.appendChild(opt);
    });
}

function populateFilters() {
    const { channels, genres, years } = collectFilterValues(allVideos);
    fillSelect(document.getElementById('channel-filter'), channels);
    fillSelect(document.getElementById('genre-filter'), genres);
    fillSelect(document.getElementById('year-filter'), years);
}

function getSelectedValues(id) {
    return Array.from(document.getElementById(id).selectedOptions).map(o => o.value);
}

function filterVideos() {
    const selChannels = getSelectedValues('channel-filter');
    const selGenres = getSelectedValues('genre-filter');
    const selYears = getSelectedValues('year-filter');
    const selRatings = getSelectedValues('rating-filter');

    return allVideos.filter(v => {
        const ch = row(v, 'music_videoOwnerChannelTitle') || row(v, 'music_channelTitle');
        if (selChannels.length && !selChannels.includes(ch)) return false;

        if (selGenres.length) {
            const vGenres = parseList(row(v, 'genres'));
            if (!selGenres.some(g => vGenres.includes(g))) return false;
        }

        const y = row(v, 'year');
        if (selYears.length && !selYears.includes(y)) return false;

        if (selRatings.length) {
            const avg = parseFloat(row(v, 'average')) || 0;
            if (selRatings.includes('0')) {
                if (avg !== 0) return false;
            } else {
                const minRating = Math.min(...selRatings.filter(r => r !== '0').map(Number));
                if (avg < minRating) return false;
            }
        }

        return true;
    });
}

function resetFilters() {
    document.getElementById('channel-filter').selectedIndex = -1;
    document.getElementById('genre-filter').selectedIndex = -1;
    document.getElementById('year-filter').selectedIndex = -1;
    document.getElementById('rating-filter').selectedIndex = -1;
    document.getElementById('sort-select').selectedIndex = 0;
    populateFilters();
    displayFilteredVideos();
}

/* ---------- sorting ---------- */

function sortGroups(groups) {
    const sortVal = document.getElementById('sort-select').value;
    const [field, dir] = sortVal.split('-');

    groups.sort((a, b) => {
        const va = a.rows[0];
        const vb = b.rows[0];
        let cmp = 0;

        if (field === 'title') {
            const ta = (row(va, 'music_title') || '').toLowerCase();
            const tb = (row(vb, 'music_title') || '').toLowerCase();
            cmp = ta.localeCompare(tb);
        } else if (field === 'year') {
            cmp = (parseInt(row(va, 'year')) || 0) - (parseInt(row(vb, 'year')) || 0);
        } else if (field === 'rating') {
            cmp = (parseFloat(row(va, 'average')) || 0) - (parseFloat(row(vb, 'average')) || 0);
        } else if (field === 'price') {
            cmp = (parseFloat(row(va, 'lowest_price')) || 0) - (parseFloat(row(vb, 'lowest_price')) || 0);
        }

        return dir === 'desc' ? -cmp : cmp;
    });
    return groups;
}

/* ---------- grouping by etag ---------- */

function groupByEtag(videos) {
    const map = new Map();

    videos.forEach(v => {
        const etag = row(v, 'etag') || '';
        if (!map.has(etag)) {
            map.set(etag, []);
        }
        map.get(etag).push(v);
    });

    return Array.from(map.entries()).map(([etag, rows]) => ({ etag, rows }));
}

/* ---------- rendering ---------- */

function displayFilteredVideos() {
    const filtered = filterVideos();
    let groups = groupByEtag(filtered);
    groups = sortGroups(groups);
    renderGroups(groups);
}

function renderGroups(groups) {
    const resultsDiv = document.getElementById('results');

    if (!groups.length) {
        resultsDiv.innerHTML = '<p>No results found.</p>';
        return;
    }

    const totalRows = groups.reduce((s, g) => s + g.rows.length, 0);
    let html = `<p class="count-label">${groups.length} release${groups.length > 1 ? 's' : ''} (${totalRows} row${totalRows > 1 ? 's' : ''})</p>`;

    if (currentView === 'grid') {
        html += '<div class="video-grid">';
        groups.forEach(g => { html += renderCardGrid(g); });
        html += '</div>';
    } else {
        html += '<div class="video-list">';
        groups.forEach(g => { html += renderCardList(g); });
        html += '</div>';
    }

    resultsDiv.innerHTML = html;
}

function buildDiscogsBlock(v) {
    const title = escapeHtml(row(v, 'title'));
    const country = escapeHtml(row(v, 'country'));
    const year = escapeHtml(row(v, 'year'));
    const label = parseList(row(v, 'label'));
    const discogsUrl = escapeHtml(row(v, 'discord_url'));
    const genres = parseList(row(v, 'genres'));
    const styles = parseList(row(v, 'styles'));
    const price = row(v, 'lowest_price');
    const forSale = row(v, 'num_for_sale');
    const avg = row(v, 'average');
    const count = row(v, 'count');

    return `
        <div class="discogs-frame">
            <div class="discogs-header">
                <div class="discogs-title">${discogsUrl ? `<a href="${discogsUrl}" target="_blank" rel="noopener">${title || 'Unknown release'}</a>` : (title || 'Unknown release')}</div>
            </div>
            <div class="discogs-meta">
                ${country ? `<span class="tag tag-country">${country}</span>` : ''}
                ${year ? `<span class="tag tag-year">${year}</span>` : ''}
            </div>
            ${label.length ? `<div class="discogs-label">Label: ${label.map(l => escapeHtml(l)).join(', ')}</div>` : ''}
            <div class="discogs-tags">
                ${genres.map(g => `<span class="tag tag-genre">${escapeHtml(g)}</span>`).join('')}
                ${styles.map(s => `<span class="tag tag-style">${escapeHtml(s)}</span>`).join('')}
            </div>
            <div class="discogs-stats">
                ${avg && avg !== '0.0' ? `<span class="stat">★ ${avg}${count ? ' (' + count + ')' : ''}</span>` : ''}
                ${price ? `<span class="stat">From $${price}</span>` : ''}
                ${forSale && forSale !== '0' ? `<span class="stat">${forSale} for sale</span>` : ''}
            </div>
        </div>`;
}

function renderCardGrid(group) {
    const first = group.rows[0];
    const thumb = escapeHtml(row(first, 'music_url'));
    const musicTitle = escapeHtml(row(first, 'music_title'));
    const videoUrl = escapeHtml(row(first, 'VideoUrl'));
    const channel = escapeHtml(row(first, 'music_videoOwnerChannelTitle') || row(first, 'music_channelTitle'));
    const desc = escapeHtml(row(first, 'music_description'));
    const hasMultiple = group.rows.length > 1;

    let html = `<div class="video-card${hasMultiple ? ' multi' : ''}">`;
    if (thumb) {
        html += videoUrl
            ? `<a href="${videoUrl}" target="_blank" rel="noopener"><img src="${thumb}" alt="Thumbnail" class="thumbnail"></a>`
            : `<img src="${thumb}" alt="Thumbnail" class="thumbnail">`;
    }
    html += videoUrl
        ? `<h3><a href="${videoUrl}" target="_blank" rel="noopener" class="video-link">${musicTitle || 'Untitled'}</a></h3>`
        : `<h3>${musicTitle || 'Untitled'}</h3>`;
    html += channel ? `<span class="channel-name">${channel}</span>` : '';
    html += desc ? `<p class="description">${desc.substring(0, 120)}${desc.length > 120 ? '…' : ''}</p>` : '';

    if (hasMultiple) {
        html += `<div class="sub-frames-label">${group.rows.length} Discogs matches</div>`;
        html += '<div class="sub-frames">';
        group.rows.forEach(v => { html += buildDiscogsBlock(v); });
        html += '</div>';
    } else {
        html += buildDiscogsBlock(first);
    }

    html += '</div>';
    return html;
}

function renderCardList(group) {
    const first = group.rows[0];
    const thumb = escapeHtml(row(first, 'music_url'));
    const musicTitle = escapeHtml(row(first, 'music_title'));
    const videoUrl = escapeHtml(row(first, 'VideoUrl'));
    const channel = escapeHtml(row(first, 'music_videoOwnerChannelTitle') || row(first, 'music_channelTitle'));
    const desc = escapeHtml(row(first, 'music_description'));
    const hasMultiple = group.rows.length > 1;

    let html = `<div class="video-card-list${hasMultiple ? ' multi' : ''}">`;
    if (thumb) {
        html += videoUrl
            ? `<a href="${videoUrl}" target="_blank" rel="noopener"><img src="${thumb}" alt="Thumbnail" class="thumbnail"></a>`
            : `<img src="${thumb}" alt="Thumbnail" class="thumbnail">`;
    }
    html += '<div class="content">';
    html += videoUrl
        ? `<h3><a href="${videoUrl}" target="_blank" rel="noopener" class="video-link">${musicTitle || 'Untitled'}</a></h3>`
        : `<h3>${musicTitle || 'Untitled'}</h3>`;
    html += channel ? `<span class="channel-name">${channel}</span>` : '';
    html += desc ? `<p class="description">${desc.substring(0, 200)}${desc.length > 200 ? '…' : ''}</p>` : '';

    if (hasMultiple) {
        html += `<div class="sub-frames-label">${group.rows.length} Discogs matches</div>`;
        html += '<div class="sub-frames">';
        group.rows.forEach(v => { html += buildDiscogsBlock(v); });
        html += '</div>';
    } else {
        html += buildDiscogsBlock(first);
    }

    html += '</div></div>';
    return html;
}
