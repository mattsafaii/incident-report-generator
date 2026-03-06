// Report preview rendering with inline editing

function renderReport() {
  const preview = document.getElementById('report-preview');
  const a = appState.analysis;
  const location = document.getElementById('location').value || 'Not specified';
  const cameraId = document.getElementById('camera-id').value || 'Not specified';
  const now = new Date();
  const dateStr = now.toISOString().slice(0, 16).replace('T', ' ');

  // Build key frame screenshots
  const screenshotHtml = (a.key_frame_indices || []).slice(0, 4).map(idx => {
    const frame = appState.frames[idx];
    if (!frame) return '';
    return `
      <div class="report-screenshot">
        <img src="${frame.url}" alt="Frame at ${frame.timestamp}">
        <div class="caption">${frame.timestamp} — Key frame</div>
      </div>
    `;
  }).join('');

  const confidenceClass = (a.confidence || 'low').toLowerCase();

  preview.innerHTML = `
    <div class="report-header">
      <h2>SECURITY INCIDENT REPORT</h2>
      <div class="report-meta">Generated: ${dateStr}</div>
    </div>

    <div class="report-section">
      <h3>Incident Summary</h3>
      <p>
        Classification: <strong>${a.classification}</strong>
        <span class="report-badge ${confidenceClass}">${a.confidence} Confidence</span>
      </p>
      <p contenteditable="true" data-field="incident_summary">${a.incident_summary}</p>
    </div>

    <div class="report-section">
      <h3>Details</h3>
      <table class="report-details-table">
        <tr><td>Date/Time</td><td>${dateStr}</td></tr>
        <tr><td>Location</td><td>${location}</td></tr>
        <tr><td>Camera ID</td><td>${cameraId}</td></tr>
        <tr><td>Reporting Party</td><td>Automated System</td></tr>
      </table>
    </div>

    <div class="report-section">
      <h3>Timeline</h3>
      ${(a.timeline || []).map((t, i) => `
        <div class="report-timeline-entry">
          <span class="ts">${t.timestamp}</span> —
          <span contenteditable="true" data-field="timeline.${i}.description">${t.description}</span>
        </div>
      `).join('')}
    </div>

    <div class="report-section">
      <h3>Key Screenshots</h3>
      ${screenshotHtml || '<p class="hint">No key frames identified.</p>'}
    </div>

    <div class="report-section">
      <h3>Subject Description</h3>
      <p contenteditable="true" data-field="subject_description">${a.subject_description}</p>
    </div>

    <div class="report-section">
      <h3>Recommended Actions</h3>
      <ul class="report-actions-list">
        ${(a.recommended_actions || []).map((action, i) => `
          <li contenteditable="true" data-field="recommended_actions.${i}">${action}</li>
        `).join('')}
      </ul>
    </div>
  `;
}

function collectEditedData() {
  const data = JSON.parse(JSON.stringify(appState.analysis));

  document.querySelectorAll('[contenteditable][data-field]').forEach(el => {
    const field = el.dataset.field;
    const value = el.textContent.trim();

    if (field.includes('.')) {
      const parts = field.split('.');
      let target = data;
      for (let i = 0; i < parts.length - 1; i++) {
        const key = isNaN(parts[i]) ? parts[i] : parseInt(parts[i]);
        target = target[key];
      }
      target[parts[parts.length - 1]] = value;
    } else {
      data[field] = value;
    }
  });

  // Add metadata
  data.location = document.getElementById('location').value || null;
  data.camera_id = document.getElementById('camera-id').value || null;

  return data;
}
