

/* ========== Gestion des tuiles/catégories ========== */

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


