setInterval(() => {
    let selfie = document.getElementById("selfie_img");
    selfie.src = "/static/selfie.jpg?t=" + new Date().getTime(); // Prevents caching
}, 3000);

const sound = new Audio('/static/sound.mp3');
document.getElementById("selfie_img").addEventListener("click", () => {
    sound.play();
});
