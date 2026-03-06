// PDF export

document.getElementById('btn-export').addEventListener('click', async () => {
  const btn = document.getElementById('btn-export');
  btn.disabled = true;
  btn.textContent = 'Generating PDF...';

  try {
    const reportData = collectEditedData();

    const resp = await fetch('/api/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_id: appState.jobId,
        report_data: reportData,
      }),
    });

    if (!resp.ok) {
      let msg = 'PDF generation failed';
      try {
        const err = await resp.json();
        msg = err.detail || msg;
      } catch {}
      throw new Error(msg);
    }

    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `incident-report-${appState.jobId.slice(0, 8)}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (err) {
    alert('PDF generation failed: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Download PDF';
  }
});

// Restart button
document.getElementById('btn-restart').addEventListener('click', () => {
  resetApp();
});
