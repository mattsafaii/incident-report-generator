// Section navigation and global state

const sections = {
  upload: document.getElementById('section-upload'),
  config: document.getElementById('section-config'),
  progress: document.getElementById('section-progress'),
  report: document.getElementById('section-report'),
};

const appState = {
  jobId: null,
  frames: [],
  analysis: null,
};

function showSection(name) {
  Object.values(sections).forEach(s => {
    s.hidden = true;
    s.classList.remove('active');
  });
  sections[name].hidden = false;
  sections[name].classList.add('active');
  window.scrollTo(0, 0);
}

function showError(message) {
  const el = document.getElementById('upload-error');
  el.textContent = message;
  el.hidden = false;
  setTimeout(() => { el.hidden = true; }, 8000);
}

function resetApp() {
  appState.jobId = null;
  appState.frames = [];
  appState.analysis = null;
  appState.durationSeconds = null;
  document.getElementById('frame-preview').innerHTML = '';
  document.getElementById('frame-section').hidden = true;
  document.getElementById('report-preview').innerHTML = '';
  document.getElementById('upload-error').hidden = true;
  document.getElementById('upload-status').hidden = true;
  const progress = document.getElementById('upload-progress');
  progress.hidden = true;
  progress.querySelector('.progress-fill').style.width = '0%';
  document.getElementById('file-input').value = '';
  showSection('upload');
}
