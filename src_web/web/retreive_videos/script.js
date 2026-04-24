document.getElementById('retrieve-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const search = document.getElementById('search').value.trim();
    if (!search) {
        alert('Please enter a search term');
        return;
    }
    
    const type = document.getElementById('type').value;
    const saveToDb = document.getElementById('save-db').checked ? 'true' : 'false';
    
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<p>Retrieving videos...</p>';
    
    fetch(`/api/get_videos/${encodeURIComponent(search)}/${type}/${saveToDb}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                displayVideos(data.videos, data.header);
            } else {
                resultsDiv.innerHTML = '<p>❌ Error retrieving videos. Please try again.</p>';
            }
        })
        .catch(error => {
            resultsDiv.innerHTML = '<p>❌ Error: ' + error.message + '</p>';
        });
});

function displayVideos(videos, header) {
    const resultsDiv = document.getElementById('results');
    if (!videos || videos.length === 0) {
        resultsDiv.innerHTML = '<p>No videos found.</p>';
        return;
    }
    
    let html = `<p>✅ Retrieved ${videos.length} videos successfully!</p><div class="video-grid">`;
    
    videos.forEach(video => {
        const videoObj = {};
        header.forEach((key, index) => {
            videoObj[key] = video[index];
        });
        
        html += `
            <div class="video-card">
                <h3>${videoObj.title || 'Untitled'}</h3>
                <p>${videoObj.description ? videoObj.description.substring(0, 100) + '...' : 'No description'}</p>
                ${videoObj.url ? `<a href="${"https://www.youtube.com/watch?v=" + videoObj.videoId}" target="_blank">Watch Video</a>` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    resultsDiv.innerHTML = html;
}
