const socket = io('http://localhost:5000');

const badge = document.getElementById('status-badge');
const brightnessSlider = document.getElementById('brightness');
const colorTempSlider = document.getElementById('color-temp');
const colorTempControl = document.getElementById('color-temp-control');
const modeToggle = document.getElementById('mode-toggle');

// ── Status badge ─────────────────────────────────────────────────────────────

function applyStatus({ color, text }) {
  badge.textContent = text;
  badge.className = `badge ${color}`;
}

// Load status + initial mode on page open
fetch('/status')
  .then(r => r.json())
  .then(data => {
    applyStatus(data);
    setMode(data.mode === 'manual');
  })
  .catch(() => { badge.textContent = 'Unavailable'; });

// Live updates from the server
socket.on('status_update', applyStatus);

// ── Mode toggle ───────────────────────────────────────────────────────────────

function setMode(isManual) {
  modeToggle.checked = isManual;
  colorTempControl.classList.toggle('disabled', !isManual);
  colorTempSlider.disabled = !isManual;
}

modeToggle.addEventListener('change', () => {
  const mode = modeToggle.checked ? 'manual' : 'auto';
  setMode(modeToggle.checked);
  socket.emit('mode_change', { mode });
});

// ── Sliders (debounced) ───────────────────────────────────────────────────────

function debounce(fn, ms) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); };
}

brightnessSlider.addEventListener('input', debounce(e => {
  socket.emit('brightness_change', { value: Number(e.target.value) });
}, 120));

colorTempSlider.addEventListener('input', debounce(e => {
  socket.emit('color_temp_change', { value: Number(e.target.value) });
}, 120));
