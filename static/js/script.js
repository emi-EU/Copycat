const videoInput = document.getElementById('videoInput');
const preview = document.getElementById('preview');
const downloadLink = document.getElementById('downloadLink');
const logBox = document.getElementById('log');

let selectedFile = null;

videoInput.addEventListener('change', () => {
  selectedFile = videoInput.files[0];
  if (selectedFile) {
    const url = URL.createObjectURL(selectedFile);
    preview.src = url;
    logBox.innerText = `Vidéo chargée : ${selectedFile.name}`;
    downloadLink.style.display = 'none';
  }
});

async function applyEffects() {
  if (!selectedFile) return alert("Choisis une vidéo MP4 !");
  logBox.innerText = "Traitement en cours...";

  const formData = new FormData();
  formData.append("video", selectedFile);
  formData.append("watermark", document.getElementById('watermarkText').value);
  formData.append("opacity", document.getElementById('opacity').value);
  formData.append("borderColor", document.getElementById('borderColor').value);
  formData.append("borderWidth", document.getElementById('borderWidth').value);

  try {
    const res = await fetch("/process", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error(await res.text());

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    preview.src = url;
    downloadLink.href = url;
    downloadLink.style.display = 'inline-block';
    logBox.innerText = "✅ Vidéo prête ! Clique sur télécharger.";
  } catch (err) {
    console.error(err);
    logBox.innerText = "❌ Erreur : " + err.message;
  }
}
