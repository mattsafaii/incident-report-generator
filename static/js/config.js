// Provider selection, API key persistence, and conditional frame extraction

const providerSelect = document.getElementById('provider');
const googleKeyInput = document.getElementById('google-api-key');
const anthropicKeyInput = document.getElementById('api-key');
const googleKeyField = document.getElementById('field-google-key');
const anthropicKeyField = document.getElementById('field-anthropic-key');
const providerHint = document.getElementById('provider-hint');
const frameSection = document.getElementById('frame-section');

const PROVIDER_HINTS = {
  gemini: 'Gemini analyzes the full video natively for better results.',
  claude: 'Claude analyzes selected frames using vision.',
};

let framesLoaded = false;

function updateProviderUI() {
  const provider = providerSelect.value;
  googleKeyField.hidden = provider !== 'gemini';
  anthropicKeyField.hidden = provider !== 'claude';
  providerHint.textContent = PROVIDER_HINTS[provider] || '';
  localStorage.setItem('provider', provider);
}

async function onProviderChange() {
  updateProviderUI();
  const provider = providerSelect.value;

  if (provider === 'claude' && appState.jobId) {
    frameSection.hidden = false;
    if (!framesLoaded) {
      await extractFrames();
    }
  } else {
    frameSection.hidden = true;
  }
}

async function extractFrames() {
  const grid = document.getElementById('frame-preview');
  grid.innerHTML = '<p class="hint">Extracting frames...</p>';
  document.getElementById('frame-count').textContent = '';

  try {
    const resp = await fetch(`/api/extract-frames/${appState.jobId}`, { method: 'POST' });
    if (!resp.ok) {
      let msg = 'Frame extraction failed';
      try {
        const err = await resp.json();
        msg = err.detail || msg;
      } catch {}
      throw new Error(msg);
    }

    const data = await resp.json();
    appState.frames = data.frames;
    framesLoaded = true;

    renderFramePreview(data.frames);
    document.getElementById('frame-count').textContent =
      `(${data.selected_frame_count} of ${data.total_frames_extracted} selected)`;
  } catch (err) {
    grid.innerHTML = '';
    showError(err.message);
  }
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

// Load saved values
providerSelect.value = localStorage.getItem('provider') || 'gemini';
googleKeyInput.value = localStorage.getItem('google_api_key') || '';
anthropicKeyInput.value = localStorage.getItem('anthropic_api_key') || '';
updateProviderUI();

// Save on change
providerSelect.addEventListener('change', onProviderChange);
googleKeyInput.addEventListener('input', () => {
  localStorage.setItem('google_api_key', googleKeyInput.value);
});
anthropicKeyInput.addEventListener('input', () => {
  localStorage.setItem('anthropic_api_key', anthropicKeyInput.value);
});

// Restart button
document.getElementById('btn-restart-config').addEventListener('click', () => {
  framesLoaded = false;
  resetApp();
});
