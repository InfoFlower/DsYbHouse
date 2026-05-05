document.addEventListener('DOMContentLoaded', function() {
    check_login();
    document.getElementById('login-form').addEventListener('submit', Send_login);
    // document.getElementById('login').addEventListener('click', display_login);
    document.getElementById('rated-btn').addEventListener('click', Show_rated);
    document.getElementById('unrated-btn').addEventListener('click', Show_unrated);
    document.getElementById('select-unrated-video-btn').addEventListener('click', make_swipper);
    document.getElementById('submit-rating-btn').addEventListener('click', submit_rating);
    document.getElementById('open-tile-selector').addEventListener('click', open_tile_selector);
});
// function display_login() {
//     const loginForm = document.getElementById('login-section');
//     loginForm.style.display = 'block';
// }

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
    const swipe_parameter = document.getElementById('unrated-selector');
    swipe_parameter.style.display = 'none';
}
function Show_unrated() {
    const swipe_parameter = document.getElementById('unrated-selector');
    swipe_parameter.style.display = 'block';
}

function make_swipper() {
    const video_selector = document.getElementById('select-video-section');
    video_selector.style.display = 'none';
    const swipper = document.getElementById('swipper');
    swipper.style.display = 'flex';
    get_unrated_video();
}

function get_unrated_video() {
    const passphrase = localStorage.getItem('passphrase');
    fetch(`/api/get_unrated_video/${passphrase}`)
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
    src="https://www.youtube.com/embed/${music.music_id}?autoplay=1&mute=1&controls=1"
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