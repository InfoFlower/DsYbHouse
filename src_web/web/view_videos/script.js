let allVideos = [];
let allHeader = [];
let currentView = 'grid'; // 'grid' or 'list'

document.addEventListener('DOMContentLoaded', function() {
    loadSavedVideos();
    
    // Add event listeners for filters
    document.getElementById('title-filter').addEventListener('change', function() {
        updateChannelFilter();
        displayFilteredVideos();
    });
    document.getElementById('channel-filter').addEventListener('change', function() {
        updateTitleFilter();
        displayFilteredVideos();
    });
    document.getElementById('reset-btn').addEventListener('click', resetFilters);
    
    // Add event listener for view toggle
    document.getElementById('view-toggle').addEventListener('click', toggleView);
});

function toggleView() {
    const toggleBtn = document.getElementById('view-toggle');
    const iconContainer = toggleBtn.querySelector('.icon-squares') || toggleBtn.querySelector('.icon-lines');
    
    if (currentView === 'grid') {
        currentView = 'list';
        // Change icon to lines
        iconContainer.className = 'icon-lines';
        iconContainer.innerHTML = `
            <div class="line"></div>
            <div class="line"></div>
            <div class="line"></div>
        `;
    } else {
        currentView = 'grid';
        // Change icon to squares
        iconContainer.className = 'icon-squares';
        iconContainer.innerHTML = `
            <div class="square"></div>
            <div class="square"></div>
            <div class="square"></div>
            <div class="square"></div>
        `;
    }
    
    // Re-display videos with new view
    displayFilteredVideos();
}

function populateFilters() {
    const titles = new Set();
    const channels = new Set();
    
    allVideos.forEach(video => {
        const videoObj = {};
        allHeader.forEach((key, index) => {
            videoObj[key] = video[index];
        });
        
        if (videoObj.title) titles.add(videoObj.title);
        if (videoObj.videoOwnerChannelTitle) channels.add(videoObj.videoOwnerChannelTitle);
    });
    
    // Clear existing options (except placeholder)
    const titleSelect = document.getElementById('title-filter');
    while (titleSelect.options.length > 1) {
        titleSelect.remove(1);
    }
    
    // Populate title filter
    titles.forEach(title => {
        const option = document.createElement('option');
        option.value = title;
        option.textContent = title;
        titleSelect.appendChild(option);
    });
    
    // Clear existing options (except placeholder)
    const channelSelect = document.getElementById('channel-filter');
    while (channelSelect.options.length > 1) {
        channelSelect.remove(1);
    }
    
    // Populate channel filter
    channels.forEach(channel => {
        const option = document.createElement('option');
        option.value = channel;
        option.textContent = channel;
        channelSelect.appendChild(option);
    });
}

function updateTitleFilter() {
    const channelSelect = document.getElementById('channel-filter');
    const selectedChannels = Array.from(channelSelect.selectedOptions).map(option => option.value);
    
    const availableTitles = new Set();
    
    allVideos.forEach(video => {
        const videoObj = {};
        allHeader.forEach((key, index) => {
            videoObj[key] = video[index];
        });
        if (selectedChannels.length === 0 || selectedChannels.includes(videoObj.videoOwnerChannelTitle)) {
            if (videoObj.title) availableTitles.add(videoObj.title);
        }
    });
    const titleSelect = document.getElementById('title-filter');
    for (let i = titleSelect.options.length - 1; i >= 1; i--) {
        const option = titleSelect.options[i];
        if (!availableTitles.has(option.value)) {
            titleSelect.remove(i);
        }
    }
    availableTitles.forEach(title => {
        if (!Array.from(titleSelect.options).some(opt => opt.value === title)) {
            const option = document.createElement('option');
            option.value = title;
            option.textContent = title;
            titleSelect.appendChild(option);
        }
    });
}

function updateChannelFilter() {
    const titleSelect = document.getElementById('title-filter');
    const selectedTitles = Array.from(titleSelect.selectedOptions).map(option => option.value);
    
    const availableChannels = new Set();
    
    allVideos.forEach(video => {
        const videoObj = {};
        allHeader.forEach((key, index) => {
            videoObj[key] = video[index];
        });
        if (selectedTitles.length === 0 || selectedTitles.includes(videoObj.title)) {
            if (videoObj.videoOwnerChannelTitle) availableChannels.add(videoObj.videoOwnerChannelTitle);
        }
    });
    
    const channelSelect = document.getElementById('channel-filter');
    for (let i = channelSelect.options.length - 1; i >= 1; i--) {
        const option = channelSelect.options[i];
        if (!availableChannels.has(option.value)) {
            channelSelect.remove(i);
        }
    }
    availableChannels.forEach(channel => {
        if (!Array.from(channelSelect.options).some(opt => opt.value === channel)) {
            const option = document.createElement('option');
            option.value = channel;
            option.textContent = channel;
            channelSelect.appendChild(option);
        }
    });
}

function loadSavedVideos() {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<div class="spinner"></div><p>Loading saved videos...</p>';
    
    fetch('/api/see_database/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                allVideos = data.videos;
                allHeader = data.header;
                populateFilters();
                displayVideos(allVideos, allHeader);
            } else {
                resultsDiv.innerHTML = '<p>❌ Error loading videos. Please try again.</p>';
            }
        })
        .catch(error => {
            resultsDiv.innerHTML = '<p>❌ Error: ' + error.message + '</p>';
        });
}

function applyFilters() {
    const titleSelect = document.getElementById('title-filter');
    const channelSelect = document.getElementById('channel-filter');
    
    const selectedTitles = Array.from(titleSelect.selectedOptions).map(option => option.value);
    const selectedChannels = Array.from(channelSelect.selectedOptions).map(option => option.value);
    
    const filteredVideos = allVideos.filter(video => {
        const videoObj = {};
        allHeader.forEach((key, index) => {
            videoObj[key] = video[index];
        });
        
        const titleMatch = selectedTitles.length === 0 || selectedTitles.includes(videoObj.title);
        const channelMatch = selectedChannels.length === 0 || selectedChannels.includes(videoObj.videoOwnerChannelTitle);
        
        return titleMatch && channelMatch;
    });
    
    displayVideos(filteredVideos, allHeader);
}

function displayFilteredVideos() {
    const titleSelect = document.getElementById('title-filter');
    const channelSelect = document.getElementById('channel-filter');
    
    const selectedTitles = Array.from(titleSelect.selectedOptions).map(option => option.value);
    const selectedChannels = Array.from(channelSelect.selectedOptions).map(option => option.value);
    
    const filteredVideos = allVideos.filter(video => {
        const videoObj = {};
        allHeader.forEach((key, index) => {
            videoObj[key] = video[index];
        });
        
        // If a channel is selected, show all videos from that channel (ignore title filter)
        if (selectedChannels.length > 0) {
            return selectedChannels.includes(videoObj.videoOwnerChannelTitle);
        }
        if (selectedTitles.length > 0) {
            return selectedTitles.includes(videoObj.title);
        }
        
        // If nothing is selected, show all videos
        return true;
    });
    
    displayVideos(filteredVideos, allHeader);
}

function resetFilters() {
    // Clear all selections
    document.getElementById('title-filter').selectedIndex = -1;
    document.getElementById('channel-filter').selectedIndex = -1;
    
    // Repopulate all options
    const titles = new Set();
    const channels = new Set();
    
    allVideos.forEach(video => {
        const videoObj = {};
        allHeader.forEach((key, index) => {
            videoObj[key] = video[index];
        });
        
        if (videoObj.title) titles.add(videoObj.title);
        if (videoObj.videoOwnerChannelTitle) channels.add(videoObj.videoOwnerChannelTitle);
    });
    
    // Clear and repopulate title filter
    const titleSelect = document.getElementById('title-filter');
    while (titleSelect.options.length > 1) {
        titleSelect.remove(1);
    }
    titles.forEach(title => {
        const option = document.createElement('option');
        option.value = title;
        option.textContent = title;
        titleSelect.appendChild(option);
    });
    
    // Clear and repopulate channel filter
    const channelSelect = document.getElementById('channel-filter');
    while (channelSelect.options.length > 1) {
        channelSelect.remove(1);
    }
    channels.forEach(channel => {
        const option = document.createElement('option');
        option.value = channel;
        option.textContent = channel;
        channelSelect.appendChild(option);
    });
    
    // Display all videos
    displayVideos(allVideos, allHeader);
}

function displayVideos(videos, header, view = currentView) {
    const resultsDiv = document.getElementById('results');
    if (!videos || videos.length === 0) {
        resultsDiv.innerHTML = '<p>No saved videos found.</p>';
        return;
    }
    
    let html = `<p>📚 ${videos.length} saved videos</p>`;
    
    if (view === 'grid') {
        html += '<div class="video-grid">';
        videos.forEach(video => {
            const videoObj = {};
            header.forEach((key, index) => {
                videoObj[key] = video[index];
            });
            
            html += `
                <div class="video-card">
                    ${videoObj.url ? `<img src="${videoObj.url}" alt="Thumbnail" class="thumbnail">` : ''}
                    <h3>${videoObj.title || 'Untitled'}</h3>
                    <p>${videoObj.description ? videoObj.description.substring(0, 100) + '...' : 'No description'}</p>
                    ${videoObj.videoId ? `<a href="https://www.youtube.com/watch?v=${videoObj.videoId}" target="_blank">Watch Video</a>` : ''}
                </div>
            `;
        });
        html += '</div>';
    } else {
        html += '<div class="video-list">';
        videos.forEach(video => {
            const videoObj = {};
            header.forEach((key, index) => {
                videoObj[key] = video[index];
            });
            
            html += `
                <div class="video-card-list">
                    ${videoObj.url ? `<img src="${videoObj.url}" alt="Thumbnail" class="thumbnail">` : ''}
                    <div class="content">
                        <h3>${videoObj.title || 'Untitled'}</h3>
                        <p>${videoObj.description || 'No description'}</p>
                        ${videoObj.videoId ? `<a href="https://www.youtube.com/watch?v=${videoObj.videoId}" target="_blank">Watch Video</a>` : ''}
                    </div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    resultsDiv.innerHTML = html;
}