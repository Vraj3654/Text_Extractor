document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const loading = document.getElementById('loading');
    const resultSection = document.getElementById('result-section');
    const rawText = document.getElementById('raw-text');
    const correctedText = document.getElementById('corrected-text');
    const imagePreview = document.getElementById('image-preview');
    const historyList = document.getElementById('history-list');

    // Load History on start
    fetchHistory();

    // Drag and Drop Events
    dropZone.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        let dt = e.dataTransfer;
        let files = dt.files;
        if (files.length) handleFiles(files[0]);
    });

    fileInput.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            handleFiles(this.files[0]);
        }
    });

    function handleFiles(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file.');
            return;
        }

        // Preview image
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'inline-block';
        }
        reader.readAsDataURL(file);

        // Upload
        uploadImage(file);
    }

    async function uploadImage(file) {
        const formData = new FormData();
        formData.append('file', file);

        // UI State
        dropZone.classList.add('hidden');
        loading.classList.remove('hidden');
        resultSection.classList.add('hidden');

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                rawText.value = data.raw_text;
                correctedText.value = data.corrected_text;
                resultSection.classList.remove('hidden');
                fetchHistory(); // Refresh history
            } else {
                alert(`Error: ${data.detail || 'Failed to process image'}`);
            }
        } catch (error) {
            console.error('Upload Error:', error);
            alert('An error occurred while communicating with the server.');
        } finally {
            loading.classList.add('hidden');
            dropZone.classList.remove('hidden');
        }
    }

    async function fetchHistory() {
        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            
            historyList.innerHTML = '';
            
            if (data.length === 0) {
                historyList.innerHTML = '<p style="color:var(--text-muted)">No processing history yet.</p>';
                return;
            }

            data.forEach(item => {
                const date = new Date(item.created_at).toLocaleString();
                const div = document.createElement('div');
                div.className = 'history-item';
                div.innerHTML = `
                    <div>
                        <p>${item.filename}</p>
                        <p>${date}</p>
                    </div>
                `;
                
                // Clicking history views it
                div.addEventListener('click', () => {
                    rawText.value = item.raw_text;
                    correctedText.value = item.corrected_text;
                    resultSection.classList.remove('hidden');
                    
                    // Hide loading spinner and show dropzone if they were in an incorrect state
                    loading.classList.add('hidden');
                    dropZone.classList.remove('hidden');
                    
                    // We don't have a direct frontend path for the DB image, so we hide the preview for history
                    imagePreview.style.display = 'none';
                    
                    window.scrollTo({ top: resultSection.offsetTop, behavior: 'smooth' });
                });

                historyList.appendChild(div);
            });
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    }
});
