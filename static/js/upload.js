// Drag-and-drop video upload with progress

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadProgress = document.getElementById('upload-progress');
const uploadStatus = document.getElementById('upload-status');

const VALID_EXTENSIONS = ['.mp4', '.mov', '.mkv', '.avi'];
const MAX_SIZE_BYTES = 500 * 1024 * 1024;

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  if (e.dataTransfer.files.length > 0) {
    handleFile(e.dataTransfer.files[0]);
  }
});

dropZone.addEventListener('click', () => {
  fileInput.click();
});

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    handleFile(fileInput.files[0]);
  }
});

function handleFile(file) {
  document.getElementById('upload-error').hidden = true;

  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!VALID_EXTENSIONS.includes(ext)) {
    showError(`Unsupported format: ${ext}. Accepted: MP4, MOV, MKV, AVI`);
    return;
  }
  if (file.size > MAX_SIZE_BYTES) {
    showError('File exceeds 500MB limit');
    return;
  }

  uploadFile(file);
}

function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  uploadProgress.hidden = false;
  uploadStatus.hidden = true;
  const fill = uploadProgress.querySelector('.progress-fill');
  const text = uploadProgress.querySelector('.progress-text');

  const xhr = new XMLHttpRequest();

  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable) {
      const pct = (e.loaded / e.total) * 100;
      fill.style.width = pct + '%';
      text.textContent = `Uploading... ${Math.round(pct)}%`;
    }
  });

  xhr.addEventListener('load', () => {
    if (xhr.status >= 200 && xhr.status < 300) {
      fill.style.width = '100%';
      text.textContent = 'Processing video...';

      const data = JSON.parse(xhr.responseText);
      appState.jobId = data.job_id;
      appState.frames = data.frames;

      // Show status
      uploadStatus.textContent =
        `Extracted ${data.total_frames_extracted} frames (${data.duration_seconds}s video). ` +
        `${data.selected_frame_count} frames selected for analysis.`;
      uploadStatus.hidden = false;

      // Populate frame preview
      renderFramePreview(data.frames);
      document.getElementById('frame-count').textContent =
        `(${data.selected_frame_count} of ${data.total_frames_extracted} selected)`;

      showSection('config');
    } else {
      let msg = 'Upload failed';
      try {
        const err = JSON.parse(xhr.responseText);
        msg = err.detail || msg;
      } catch {}
      showError(msg);
      uploadProgress.hidden = true;
    }
  });

  xhr.addEventListener('error', () => {
    showError('Upload failed. Check your connection and try again.');
    uploadProgress.hidden = true;
  });

  xhr.open('POST', '/api/upload');
  xhr.send(formData);
}

function renderFramePreview(frames) {
  const grid = document.getElementById('frame-preview');
  grid.innerHTML = '';

  frames.forEach(frame => {
    const div = document.createElement('div');
    div.className = 'frame-thumb' + (frame.selected ? ' selected' : '');
    div.innerHTML = `
      <img src="${frame.url}" alt="Frame at ${frame.timestamp}" loading="lazy">
      <div class="frame-label">
        <span>${frame.timestamp}</span>
        <span>${frame.selected ? 'Selected' : ''}</span>
      </div>
    `;
    grid.appendChild(div);
  });
}
