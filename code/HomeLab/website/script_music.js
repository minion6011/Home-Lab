document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".audio-player").forEach(player => {
        const audio = player.querySelector(".audio");
        const playPauseButton = player.querySelector(".play-pause");
        const progressBar = player.querySelector(".progress-bar");
        const volumeBar = player.querySelector(".volume-bar");
        const volumeToggle = player.querySelector(".volume-toggle");
        const loopToggle = player.querySelector(".loop-toggle");
        const moreOptions = player.querySelector(".more-options");
        const menu = player.querySelector(".menu");
        const deleteSong = player.querySelector(".delete-song");
        const currentTimeSpan = player.querySelector(".current-time");
        const durationSpan = player.querySelector(".duration");
        
        playPauseButton.addEventListener("click", () => {
            if (audio.paused) {
                audio.play();
                playPauseButton.textContent = "⏸";
            } else {
                audio.pause();
                playPauseButton.textContent = "▶";
            }
        });
        
        audio.addEventListener("loadedmetadata", () => {
            durationSpan.textContent = formatTime(audio.duration);
            progressBar.max = Math.floor(audio.duration);
        });
        
        audio.addEventListener("timeupdate", () => {
            progressBar.value = Math.floor(audio.currentTime);
            currentTimeSpan.textContent = formatTime(audio.currentTime);
        });
        
        progressBar.addEventListener("input", () => {
            audio.currentTime = progressBar.value;
        });
        
        volumeBar.addEventListener("input", () => {
            audio.volume = volumeBar.value / 100;
            volumeToggle.textContent = volumeBar.value == 0 ? "🔇" : "🔊";
        });
        
        volumeToggle.addEventListener("click", () => {
            if (audio.muted || audio.volume === 0) {
                audio.muted = false;
                audio.volume = 0.5;
                volumeBar.value = 50;
                volumeToggle.textContent = "🔊";
            } else {
                audio.muted = true;
                volumeBar.value = 0;
                volumeToggle.textContent = "🔇";
            }
        });
        
        loopToggle.addEventListener("click", () => {
            audio.loop = !audio.loop;
            loopToggle.classList.toggle("active", audio.loop);
        });
        
        moreOptions.addEventListener("click", (event) => {
            event.stopPropagation();
            menu.style.display = menu.style.display === "block" ? "none" : "block";
        });
        
        document.addEventListener("click", (event) => {
            if (!moreOptions.contains(event.target) && !menu.contains(event.target)) {
                menu.style.display = "none";
            }
        });
        
        deleteSong.addEventListener("click", () => {
            const url = deleteSong.getAttribute("data-url");
        
            fetch(url, { method: "GET" })
                .then(response => response.json())
                .then(data => {
                    window.location.href = "/music";
                });
        });
    });
});

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs < 10 ? "0" : ""}${secs}`;
}
