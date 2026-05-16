/* ========== RATED SONGS: chargement, filtres, interactions ========== */

// Charge la liste des musiques notées depuis l'API
function load_rated_songs(filters = {}) {
    const passphrase = localStorage.getItem('housify_pass');
    const query = new URLSearchParams(filters).toString();
    fetch(`/api/get_rated_videos/${passphrase}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                render_rated_songs(data.videos);
            } else {
                document.getElementById('rated-songs-grid').innerHTML = '<p>Erreur de chargement.</p>';
            }
        })
        .catch(err => {
            console.error(err);
            document.getElementById('rated-songs-grid').innerHTML = '<p>Impossible de contacter le serveur.</p>';
        });
}

// Remplit dynamiquement le filtre de catégorie avec les tiles disponibles
function populate_category_filter() {
    fetch('/api/get_tiles/')
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success' && data.active_tiles) {
                const select = document.getElementById('rated-category-filter');
                select.innerHTML = '<option value="">All Categories</option>';
                data.active_tiles.forEach(item => {
                    const opt = document.createElement('option');
                    opt.value = item.tile_name;
                    opt.textContent = item.tile_name;
                    select.appendChild(opt);
                });
            }
        });
}

// Génère la grille de cartes
function render_rated_songs(videos) {
    const grid = document.getElementById('rated-songs-grid');
    document.getElementById('rated-songs-grid').style.display = 'block';
    if (!videos || videos.length === 0) {
        grid.innerHTML = '<p style="color: rgba(255,255,255,0.4); font-style: italic;">Aucune chanson notée trouvée.</p>';
        return;
    }

    grid.innerHTML = videos.map(video => {
        const thumb = `https://img.youtube.com/vi/${video.music_id}/mqdefault.jpg`;
        const tiles = (video.tiles || []).map(t => `<span class="tile-badge">${t}</span>`).join('');
        const stars = '★'.repeat(video.rating) + '☆'.repeat(5 - video.rating);
        return `
        <div class="song-card" data-etag="${video.etag}">
            <img class="card-thumb" src="${thumb}" alt="Miniature" onclick="preview_video('${video.music_id}', '${video.music_title.replace(/'/g, "\\'")}')">
            <div class="card-header">
                <h4>${video.music_title}</h4>
                <span class="rating-stars">${stars}</span>
            </div>
            <div class="tiles-list">${tiles || '<span style="color: rgba(255,255,255,0.3); font-size:0.8rem;">aucun mot-clé</span>'}</div>
            <div class="card-actions">
                <input type="checkbox" class="checkbox-select" data-etag="${video.etag}" onchange="toggle_group_selection()">
                <button onclick="preview_video('${video.music_id}', '${video.music_title.replace(/'/g, "\\'")}')" title="Écouter">▶️</button>
                <button onclick="edit_rating('${video.etag}')" title="Modifier la note">✏️</button>
                <button onclick="alert('Work in progress')" title="Supprimer">🗑️</button>
            </div>
        </div>`;
    }).join('');
}

// Affiche la vidéo dans le player modal
function preview_video(music_id, title) {
    const modal = document.getElementById('player-modal');
    const iframe = modal.querySelector('iframe');
    iframe.src = `https://www.youtube.com/embed/${music_id}?controls=1`;
    document.getElementById('player-title').textContent = title;
    modal.style.display = 'flex';
}

// Placeholder pour l'édition de la note
function edit_rating(etag) {
    alert(`Work in progress - Modifier la note pour ${etag}`);
}



// Gestion de la sélection groupée
function toggle_group_selection() {
    const checkboxes = document.querySelectorAll('#rated-songs-grid .checkbox-select');
    const anyChecked = Array.from(checkboxes).some(cb => cb.checked);
    document.getElementById('group-actions-bar').style.display = anyChecked ? 'flex' : 'none';
}