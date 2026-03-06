// API key persistence in localStorage

const apiKeyInput = document.getElementById('api-key');

// Load saved key on page load
apiKeyInput.value = localStorage.getItem('anthropic_api_key') || '';

// Save on input
apiKeyInput.addEventListener('input', () => {
  localStorage.setItem('anthropic_api_key', apiKeyInput.value);
});

// Restart button
document.getElementById('btn-restart-config').addEventListener('click', () => {
  resetApp();
});
