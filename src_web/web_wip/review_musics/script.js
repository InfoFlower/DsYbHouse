/* ========== Initialisation et Navigation ========== */

document.addEventListener('DOMContentLoaded', async function() {
    await App.loadPartial('#admin-panel-placeholder', '../admin_panel/admin_panel.html');
    await App.loadPartial('#selector-placeholder','partials/selector.html')
    await App.loadPartial('#unrated-selector-placeholder','./partials/unrated-selector.html')
    await App.loadPartial('#rated-songs-placeholder','./partials/rated-songs.html')
    await App.loadPartial('#swipper-placeholder','./partials/swipper.html')
    await App.loadPartial('#modal-player-placeholder','/partials/modal-player.html')
    
    // Event listeners pour les boutons de sélection
    document.getElementById('rated-btn').addEventListener('click', Show_rated);
    document.getElementById('unrated-btn').addEventListener('click', Show_unrated);
    document.getElementById('select-unrated-video-btn').addEventListener('click', make_swipper);
    document.getElementById('apply-rated-filters-btn').addEventListener('click', filter_rated_songs);
    document.getElementById('back-btn').addEventListener('click', Back_to_selection);
    document.getElementById('submit-rating-btn').addEventListener('click', submit_rating);
});

// Afficher les chansons notées
function Show_rated() {
    document.getElementById('select-video-section').style.display = 'none';
    document.getElementById('swipper').style.display = 'none';
    document.getElementById('rated-selector').style.display = 'block';
    document.getElementById('back-btn').style.display = 'block';
    load_rated_songs();          // premier affichage sans filtre
    populate_category_filter();  // remplit le filtre catégorie
}

// Afficher les vidéos non notées
function Show_unrated() {
    const swipe_parameter = document.getElementById('unrated-selector');
    swipe_parameter.style.display = 'block';
}

// Lancer le swiper
function make_swipper() {
    const video_selector = document.getElementById('select-video-section');
    video_selector.style.display = 'none';
    document.getElementById('unrated-selector').style.display = 'none';
    document.getElementById('back-btn').style.display = 'block';
    const swipper = document.getElementById('swipper');
    swipper.style.display = 'flex';
    get_unrated_video();
}

// Revenir à la sélection
function Back_to_selection() {
    document.getElementById('rated-selector').style.display = 'none';
    document.getElementById('unrated-selector').style.display = 'none';
    document.getElementById('rated-songs-grid').style.display = 'none';
    document.getElementById('swipper').style.display = 'none';
    document.getElementById('back-btn').style.display = 'none';
    document.getElementById('select-video-section').style.display = 'block';
}

// Filtre les chansons notées
function filter_rated_songs() {
    const rating = document.getElementById('rated-rating-filter').value;
    const category = document.getElementById('rated-category-filter').value;
    const filters = {};
    if (rating) filters.rating = rating;
    if (category) filters.category = category;
    load_rated_songs(filters);
}

function submit_rating() {
    const passphrase = localStorage.getItem('housify_pass');
    const rating = document.getElementById('monSlider').value;
    let SelectedTiles = document.querySelectorAll('.tile.selected');
    SelectedTiles = Array.from(SelectedTiles).map(tile => tile.textContent);
    const etag = document.getElementById('swippe-card').getAttribute('data-etag');
    fetch('/api/submit_rating/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ passphrase, rating, etag, SelectedTiles })
    }).then(response => response.json())   
    .then(data => {
        if (data.status === 'success') {
            get_unrated_video();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while submitting the rating.');
    });
}

/* ========== RATED SONGS: chargement, filtres, interactions ========== */

// Charge la liste des musiques notées depuis l'API
function load_rated_songs(filters = {}) {
    const passphrase = localStorage.getItem('housify_pass');
    fetch(`/api/get_rated_videos/${passphrase}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                render_rated_songs(data.videos, filters);
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
function render_rated_songs(videos, filters = {}) {
    const grid = document.getElementById('rated-songs-grid');
    document.getElementById('rated-songs-grid')
    if (!videos || videos.length === 0) {
        grid.innerHTML = '<p style="color: rgba(255,255,255,0.4); font-style: italic;">Aucune chanson notée trouvée.</p>';
        return;
    }
    if (filters.rating) {
        videos = videos.filter(v => v.user_rating == filters.rating);
    }
    if (filters.category) {
        videos = videos.filter(v => {
            const categories = JSON.parse(v.user_category) || [];
            return categories.includes(filters.category);
        });
    }
    grid.innerHTML = videos.map(video => {
        const thumb = `https://img.youtube.com/vi/${video.music_id}/mqdefault.jpg`;
        console.log(video.user_category);
        const tiles = (JSON.parse(video.user_category) || []).map(t => `<span class="tile-badge">${t}</span>`).join('');
        const stars = '★'.repeat(video.user_rating) + '☆'.repeat(5 - video.user_rating);
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