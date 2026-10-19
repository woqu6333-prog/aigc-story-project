const audio = document.querySelector("#audioPlayer");
const transcript = document.querySelector("#transcript");
const nowPlaying = document.querySelector("#nowPlaying");
const emotionChip = document.querySelector("#emotionChip");
const followButton = document.querySelector("#followButton");
const chapterLabel = document.querySelector("#chapterLabel");
const chapterImage = document.querySelector("#chapterImage");
const heroArt = document.querySelector("#heroArt");

const chapterImages = {
  "序章": "../picturebook/assets/images/scene-01.png",
  "第一幕：奇怪的脚印": "../picturebook/assets/images/scene-01.png",
  "第二幕：蓝色羽毛": "../picturebook/assets/images/scene-02.png",
  "第三幕：回家的路": "../picturebook/assets/images/scene-03.png",
  "尾声": "../picturebook/assets/images/scene-03.png",
};

let timeline = [];
let activeIndex = -1;
let followPlayback = true;
let currentChapter = "序章";

function formatTime(seconds) {
  const value = Math.max(0, Math.floor(seconds));
  return `${Math.floor(value / 60)}:${String(value % 60).padStart(2, "0")}`;
}

function setChapter(chapter) {
  if (!chapter || chapter === currentChapter) return;
  currentChapter = chapter;
  chapterLabel.textContent = chapter;
  const source = chapterImages[chapter] || chapterImages["序章"];
  if (chapterImage.getAttribute("src") === source) return;
  heroArt.classList.add("is-changing");
  window.setTimeout(() => {
    chapterImage.src = source;
    heroArt.classList.remove("is-changing");
  }, 160);
}

function renderTimeline(data) {
  document.querySelector("#durationFact").textContent = formatTime(data.duration_seconds);
  document.querySelector("#voiceFact").textContent = data.voice_count;
  document.querySelector("#segmentFact").textContent = data.segment_count;

  const fragment = document.createDocumentFragment();
  let previousChapter = "";
  data.segments.forEach((segment, index) => {
    if (segment.chapter !== previousChapter) {
      const heading = document.createElement("h3");
      heading.className = "chapter-heading";
      heading.textContent = segment.chapter;
      fragment.appendChild(heading);
      previousChapter = segment.chapter;
    }

    const line = document.createElement("button");
    line.type = "button";
    line.className = "line";
    line.dataset.index = String(index);
    line.dataset.start = String(segment.start);
    line.setAttribute("aria-label", `从${formatTime(segment.start)}播放${segment.role}的台词`);
    line.innerHTML = `
      <span class="line-meta">
        <span class="role">${segment.role}</span>
        <span class="emotion">[${segment.emotion}]</span>
        <span class="timestamp">${formatTime(segment.start)}</span>
      </span>
      <span class="line-text">${segment.text}</span>
    `;
    line.addEventListener("click", () => {
      audio.currentTime = segment.start;
      audio.play().catch(() => {});
      updateActive(index, true);
    });
    fragment.appendChild(line);
  });
  transcript.replaceChildren(fragment);
}

function updateActive(index, forceScroll = false, suppressScroll = false) {
  if (index < 0 || index >= timeline.length || index === activeIndex) return;
  const previous = transcript.querySelector(".line.is-active");
  if (previous) previous.classList.remove("is-active");

  activeIndex = index;
  const segment = timeline[index];
  const active = transcript.querySelector(`[data-index="${index}"]`);
  if (active) {
    active.classList.add("is-active");
    if (!suppressScroll && (followPlayback || forceScroll)) {
      active.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }
  nowPlaying.textContent = `${segment.role} · ${segment.text}`;
  emotionChip.textContent = segment.emotion;
  setChapter(segment.chapter);
}

function findActiveIndex(time) {
  for (let index = timeline.length - 1; index >= 0; index -= 1) {
    if (time >= timeline[index].start) return index;
  }
  return -1;
}

audio.addEventListener("timeupdate", () => updateActive(findActiveIndex(audio.currentTime)));
audio.addEventListener("seeked", () => updateActive(findActiveIndex(audio.currentTime), true));

followButton.addEventListener("click", () => {
  followPlayback = !followPlayback;
  followButton.classList.toggle("is-active", followPlayback);
  followButton.setAttribute("aria-pressed", String(followPlayback));
  followButton.textContent = `自动跟随：${followPlayback ? "开" : "关"}`;
});

fetch("assets/audio/timeline.json")
  .then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then((data) => {
    timeline = data.segments;
    renderTimeline(data);
    if (timeline.length) {
      currentChapter = "";
      updateActive(0, false, true);
    }
  })
  .catch((error) => {
    transcript.innerHTML = `<p class="loading">时间轴加载失败：${error.message}。请使用本地服务器打开网页。</p>`;
  });
