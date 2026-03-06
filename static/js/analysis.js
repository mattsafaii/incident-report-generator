// Trigger AI analysis

document.getElementById('btn-analyze').addEventListener('click', async () => {
  const provider = document.getElementById('provider').value;
  let apiKey;

  if (provider === 'gemini') {
    apiKey = localStorage.getItem('google_api_key');
    if (!apiKey || !apiKey.trim()) {
      showError('Please enter your Google AI API key.');
      return;
    }
  } else {
    apiKey = localStorage.getItem('anthropic_api_key');
    if (!apiKey || !apiKey.trim()) {
      showError('Please enter your Anthropic API key.');
      return;
    }
  }

  if (!appState.jobId) {
    showError('No video uploaded. Please upload a video first.');
    return;
  }

  showSection('progress');

  try {
    const resp = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_id: appState.jobId,
        api_key: apiKey,
        provider: provider,
        incident_type: document.getElementById('incident-type').value || null,
        location: document.getElementById('location').value || null,
        camera_id: document.getElementById('camera-id').value || null,
      }),
    });

    if (!resp.ok) {
      let msg = 'Analysis failed';
      try {
        const err = await resp.json();
        msg = err.detail || msg;
      } catch {}
      throw new Error(msg);
    }

    const data = await resp.json();
    appState.analysis = data.analysis;
    renderReport();
    showSection('report');
  } catch (err) {
    showError(err.message);
    showSection('config');
  }
});
