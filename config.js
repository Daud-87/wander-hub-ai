// Wander Hub AI - one place for backend addresses.
// On your own computer (localhost) the local servers are used.
// When deployed, API calls go to the same site (/api/...), served by the Vercel function.
(function () {
  var local = ['localhost', '127.0.0.1'].indexOf(location.hostname) !== -1;

  // Node/Express login + signup backend
  window.WH_API_BASE = local ? 'http://localhost:5000' : '';

  // Flask AI Predictor (project-root/app.py). Paste its public URL here after hosting it
  // (for example on Render): 'https://your-ai-predictor.onrender.com'
  var AI_PREDICTOR_URL = '';
  window.WH_AI_URL = local ? 'http://127.0.0.1:5000' : AI_PREDICTOR_URL;

  // Flask translation helper (app1.py). Paste its public URL + '/helper' when hosted.
  var HELPER_URL = '';
  window.WH_HELPER_URL = local ? 'http://127.0.0.1:5001/helper' : HELPER_URL;
})();
