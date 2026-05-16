/* ========== UNRATED VIDEOS: gestion du swiper ========== */

function get_unrated_video() {
    const passphrase = localStorage.getItem('housify_pass');
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
    open_tile_selector(); 
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
