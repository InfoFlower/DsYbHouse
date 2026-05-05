document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('add-tile-btn').addEventListener('click', send_tile_data);
    document.getElementById('remove-tile-btn').addEventListener('click', remove_tile_data);
});


function send_tile_data() {
    const title = document.getElementById('new-tile-name').value;
    if (!title) {
        alert('Please enter a tile name.');
        return;
    }
    fetch('/api/add_tile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: title })
    })
    .then(response => response.json())
    .then(data => {
        // Extract the correct property: "active_tiles"
        const tilesArray = data.active_tiles || [];
        // Convert each object { tile_name: "..." } into a string
        const tileNames = tilesArray.map(item => item.tile_name);
        update_active_tiles(tileNames);
    })
    .catch(error => console.error('Error:', error));
}

function update_active_tiles(actives_tiles) {
    const actives_tiles_list = document.getElementById('active-tiles');
    if (!actives_tiles_list) return;
    actives_tiles_list.innerHTML = '';
    // Now actives_tiles is an array of strings (e.g., ["zz", "sexy", ""])
    actives_tiles.forEach(element => {
        const li = document.createElement('li');
        li.textContent = element;
        actives_tiles_list.appendChild(li);
    });
}

function remove_tile_data() {
    const title = document.getElementById('new-tile-name').value;
    fetch('/api/remove_tile/' + encodeURIComponent(title))
    .then(response => response.json())
    .then(data => {
        const tilesArray = data.active_tiles || [];
        const tileNames = tilesArray.map(item => item.tile_name);
        update_active_tiles(tileNames);
    })
    .catch(error => console.error('Error:', error));
}