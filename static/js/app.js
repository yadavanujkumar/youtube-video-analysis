document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const youtubeUrlInput = document.getElementById('youtube-url');
    const processBtn = document.getElementById('process-btn');
    const processingStatus = document.getElementById('processing-status');
    const errorMessage = document.getElementById('error-message');
    const videoInfoSection = document.getElementById('video-info-section');
    const videoThumbnail = document.getElementById('video-thumbnail');
    const videoTitle = document.getElementById('video-title');
    const videoAuthor = document.getElementById('video-author');
    const videoDescription = document.getElementById('video-description');
    const querySection = document.getElementById('query-section');
    const queryInput = document.getElementById('query-input');
    const queryBtn = document.getElementById('query-btn');
    const queryProcessing = document.getElementById('query-processing');
    const responseSection = document.getElementById('response-section');
    const queryDisplay = document.getElementById('query-display');
    const responseContent = document.getElementById('response-content');
    const queryHistory = document.getElementById('query-history');

    // Store current video ID
    let currentVideoId = null;
    
    // Event listeners
    processBtn.addEventListener('click', processVideo);
    queryBtn.addEventListener('click', processQuery);

    // Function to process video
    async function processVideo() {
        const youtubeUrl = youtubeUrlInput.value.trim();
        
        if (!youtubeUrl) {
            showError('Please enter a YouTube URL');
            return;
        }
        
        // Show processing status
        processingStatus.classList.remove('d-none');
        errorMessage.classList.add('d-none');
        videoInfoSection.classList.add('d-none');
        querySection.classList.add('d-none');
        responseSection.classList.add('d-none');
        
        try {
            const response = await fetch('/process_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ youtube_url: youtubeUrl })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Success
                processingStatus.classList.add('d-none');
                
                // Store video ID
                currentVideoId = data.video_id;
                
                // Fetch video details
                await fetchVideoDetails(currentVideoId);
                
                // Show query section
                querySection.classList.remove('d-none');
            } else {
                // Error
                showError(data.error || 'An error occurred while processing the video');
            }
        } catch (error) {
            showError('Network error: ' + error.message);
        }
    }
    
    // Function to fetch video details
    async function fetchVideoDetails(videoId) {
        try {
            const response = await fetch(`/video_details/${videoId}`);
            const data = await response.json();
            
            if (response.ok) {
                // Display video information
                videoThumbnail.src = data.thumbnail_url;
                videoTitle.textContent = data.title;
                videoAuthor.textContent = `By ${data.author}`;
                videoDescription.textContent = data.description.substring(0, 150) + '...';
                
                // Show video info section
                videoInfoSection.classList.remove('d-none');
            } else {
                showError(data.error || 'Could not fetch video details');
            }
        } catch (error) {
            showError('Error fetching video details: ' + error.message);
        }
    }
    
    // Function to process query
    async function processQuery() {
        const query = queryInput.value.trim();
        
        if (!query) {
            showError('Please enter a question');
            return;
        }
        
        if (!currentVideoId) {
            showError('No video has been processed yet');
            return;
        }
        
        // Show processing status
        queryProcessing.classList.remove('d-none');
        errorMessage.classList.add('d-none');
        responseSection.classList.add('d-none');
        
        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    video_id: currentVideoId,
                    query: query
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Hide processing status
                queryProcessing.classList.add('d-none');
                
                // Display query and response
                queryDisplay.textContent = query;
                responseContent.innerHTML = formatResponse(data.response);
                
                // Show response section
                responseSection.classList.remove('d-none');
                
                // Add to history
                addToHistory(query, data.response);
                
                // Clear input
                queryInput.value = '';
            } else {
                showError(data.error || 'An error occurred while processing your question');
            }
        } catch (error) {
            showError('Network error: ' + error.message);
        }
    }
    
    // Function to format response with simple markdown
    function formatResponse(text) {
        // Convert markdown-like syntax to HTML
        return text
            .replace(/\n\n/g, '<br><br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }
    
    // Function to add query to history
    function addToHistory(query, response) {
        const historyItem = document.createElement('li');
        historyItem.className = 'list-group-item';
        historyItem.innerHTML = `
            <p class="fw-bold mb-1">${query}</p>
            <p class="small text-truncate">${response.substring(0, 100)}...</p>
        `;
        
        // Add click event to show full response
        historyItem.addEventListener('click', function() {
            queryDisplay.textContent = query;
            responseContent.innerHTML = formatResponse(response);
            responseSection.classList.remove('d-none');
            
            // Scroll to response
            responseSection.scrollIntoView({ behavior: 'smooth' });
        });
        
        // Add to history list
        queryHistory.prepend(historyItem);
    }
    
    // Function to show error
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('d-none');
        processingStatus.classList.add('d-none');
        queryProcessing.classList.add('d-none');
    }
});