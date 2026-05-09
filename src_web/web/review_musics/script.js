document.addEventListener('DOMContentLoaded', function() {
    check_login();
    document.getElementById('login-form').addEventListener('submit', Send_login);
    // document.getElementById('login').addEventListener('click', display_login);
    document.getElementById('rated-btn').addEventListener('click', Show_rated);
    document.getElementById('unrated-btn').addEventListener('click', Show_unrated);
    document.getElementById('select-unrated-video-btn').addEventListener('click', make_swipper);
    document.getElementById('submit-rating-btn').addEventListener('click', submit_rating);
    document.getElementById('open-tile-selector').addEventListener('click', open_tile_selector);
    document.getElementById('apply-rated-filters-btn').addEventListener('click', filter_rated_songs);
    // Bouton Back pour revenir à la sélection
    document.getElementById('back-from-rated-btn').addEventListener('click', Back_to_selection);
    document.getElementById('back-from-unrated-btn').addEventListener('click', Back_to_selection);
});

function filter_rated_songs() {
    const rating = document.getElementById('rated-rating-filter').value;
    const category = document.getElementById('rated-category-filter').value;
    const filters = {};
    if (rating) filters.rating = rating;
    if (category) filters.category = category;
    load_rated_songs(filters);
}

function Back_to_selection() {
    document.getElementById('rated-selector').style.display = 'none';
    document.getElementById('unrated-selector').style.display = 'none';
    document.getElementById('rated-songs-grid').style.display = 'none';
    document.getElementById('swipper').style.display = 'none';
    document.getElementById('select-video-section').style.display = 'block';
}
function check_login() {
    const passphrase = localStorage.getItem('passphrase');
    if (passphrase) {
        fetch('/api/check_passphrase/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ passphrase })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                display_rating();
            }
        });
    }
}

function Send_login(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    fetch('/api/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    }).then(response => response.json())
  .then(data => {
    debug_section = document.getElementById('debug-section');
    if (debug_section) {
        debug_section.textContent = JSON.stringify(data, null, 2);
    }
      if (data.status === 'success') {
            if (data.passphrase) { 
                localStorage.setItem('passphrase', data.passphrase);
                display_rating();
            }
            else {
                alert('Login successful, but no passphrase received.');
            }
        }
        else {
            alert('Login failed: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during login.');
    });
}

function display_rating() {
    const loginForm = document.getElementById('login-section');
    loginForm.style.display = 'none';
    const video_selector = document.getElementById('select-video-section');
    video_selector.style.display = 'block';
}

function Show_rated() {
    document.getElementById('select-video-section').style.display = 'none';
    document.getElementById('swipper').style.display = 'none';
    document.getElementById('rated-selector').style.display = 'block';
    load_rated_songs();          // premier affichage sans filtre
    populate_category_filter();  // remplit le filtre catégorie
}

/* ========== RATED SONGS : chargement, filtres, interactions ========== */

// Charge la liste des musiques notées depuis l'API
function load_rated_songs(filters = {}) {
    const passphrase = localStorage.getItem('passphrase');
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

// Fermeture du player modal
// document.querySelector('.close-player').addEventListener('click', () => {
//     const modal = document.getElementById('player-modal');
//     const iframe = modal.querySelector('iframe');
//     iframe.src = ''; // arrête la vidéo
//     modal.style.display = 'none';
// });

// Placeholder pour l'édition de la note (sera développée plus tard)
function edit_rating(etag) {
    alert(`Work in progress - Modifier la note pour ${etag}`);
}

/* ========== Gestion de la sélection groupée ========== */
function toggle_group_selection() {
    const checkboxes = document.querySelectorAll('#rated-songs-grid .checkbox-select');
    const anyChecked = Array.from(checkboxes).some(cb => cb.checked);
    document.getElementById('group-actions-bar').style.display = anyChecked ? 'flex' : 'none';
}

// Boutons d'action groupée (placeholder)
// document.getElementById('group-edit-btn').addEventListener('click', () => {
//     const selected = Array.from(document.querySelectorAll('#rated-songs-grid .checkbox-select:checked'))
//                          .map(cb => cb.dataset.etag);
//     if (selected.length === 0) {
//         alert('Aucune chanson sélectionnée.');
//         return;
//     }
//     alert(`Work in progress - Modification groupée pour : ${selected.join(', ')}`);
// });
// document.getElementById('group-delete-btn').addEventListener('click', () => {
//     const selected = Array.from(document.querySelectorAll('#rated-songs-grid .checkbox-select:checked'))
//                          .map(cb => cb.dataset.etag);
//     if (selected.length === 0) {
//         alert('Aucune chanson sélectionnée.');
//         return;
//     }
//     alert(`Work in progress - Suppression groupée pour : ${selected.join(', ')}`);
// });

function Show_unrated() {
    const swipe_parameter = document.getElementById('unrated-selector');
    swipe_parameter.style.display = 'block';
}

function make_swipper() {
    const video_selector = document.getElementById('select-video-section');
    video_selector.style.display = 'none';
    document.getElementById('unrated-selector').style.display = 'none';
    const swipper = document.getElementById('swipper');
    swipper.style.display = 'flex';
    get_unrated_video();
}

function get_unrated_video() {
    const passphrase = localStorage.getItem('passphrase');
    const order_by = document.getElementById('unrated-videos-dropdown').value;
    fetch(`/api/get_unrated_video/${passphrase}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ order_by })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            create_swiper(data.video);
        }
    });
}

function create_swiper(music) {
    const swiper_container = document.getElementById('swipper-container');
    
    swiper_container.innerHTML = `<div class="swippe-card" id="swippe-card" data-etag="${music.etag}">
  <iframe
    src="https://www.youtube.com/embed/${music.music_id}?controls=1"
    title="YouTube video player"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen>
    </iframe>
    <h3 id="music-title">${music.music_title}</h3>
</div>
`;
}

function submit_rating() {
    const passphrase = localStorage.getItem('passphrase');
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


function open_tile_selector() {
    fetch('/api/get_tiles/')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const tiles_grid = document.getElementById('active-tiles');
            tiles_grid.innerHTML = '';
            const tilesArray = data.active_tiles || [];
        // Convert each object { tile_name: "..." } into a string
            const tileNames = tilesArray.map(item => item.tile_name);
            tileNames.forEach(tile => {
                const tile_element = document.createElement('div');
                tile_element.classList.add('tile');
                tile_element.textContent = tile;
                tile_element.addEventListener('click', function() {
                    tile_element.classList.toggle('selected');
                });
                tiles_grid.appendChild(tile_element);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while fetching tiles.');
    }
    );
}