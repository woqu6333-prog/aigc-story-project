"use strict";

const statusBox = document.querySelector("#h3Status");
const statusTitle = document.querySelector("#statusTitle");
const statusDetail = document.querySelector("#statusDetail");
const generateButton = document.querySelector("#generateButton");
const actionInput = document.querySelector("#actionInput");
const resultVideo = document.querySelector("#resultVideo");
let h3Ready = false;
let pollTimer = null;

function setStatus(state, title, detail) {
  statusBox.dataset.state = state;
  statusTitle.textContent = title;
  statusDetail.textContent = detail;
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({ message: "服务返回内容无法解析" }));
  if (!response.ok || !data.ok) throw new Error(data.message || `请求失败：${response.status}`);
  return data;
}

async function checkH3() {
  if (window.location.protocol === "file:" || window.location.hostname.endsWith("github.io")) {
    setStatus("offline", "样片播放模式", "GitHub Pages不连接本机GPU；请在本机服务中现场生成");
    return;
  }
  try {
    const data = await requestJson("/api/h3/health", { cache: "no-store" });
    h3Ready = Boolean(data.available);
    generateButton.disabled = !h3Ready;
    setStatus(h3Ready ? "ready" : "offline", data.message, h3Ready ? `${data.device} · 预计${data.estimated_seconds}秒` : "请先启动ComfyUI 8188端口");
  } catch (error) {
    setStatus("offline", "本地H3未连接", error.message);
  }
}

async function pollJob(jobId) {
  try {
    const data = await requestJson(`/api/h3/jobs/${jobId}`, { cache: "no-store" });
    const job = data.job;
    if (job.status === "completed") {
      window.clearInterval(pollTimer);
      resultVideo.src = `${job.video_url}?t=${Date.now()}`;
      resultVideo.load();
      resultVideo.play().catch(() => {});
      setStatus("ready", "新镜头生成完成", "视频已替换为本次H3生成结果");
      generateButton.disabled = false;
    } else if (job.status === "failed") {
      window.clearInterval(pollTimer);
      setStatus("offline", "生成失败", job.message);
      generateButton.disabled = false;
    } else {
      setStatus("working", "H3正在生成真实运动", job.prompt_id ? "已进入ComfyUI队列，请等待约100秒" : "正在上传参考图并准备工作流");
    }
  } catch (error) {
    window.clearInterval(pollTimer);
    setStatus("offline", "查询任务失败", error.message);
    generateButton.disabled = false;
  }
}

async function generateClip() {
  if (!h3Ready) return;
  generateButton.disabled = true;
  setStatus("working", "正在提交H3任务", "将使用小雨角色设定图与第一幕场景图");
  try {
    const data = await requestJson("/api/h3/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: actionInput.value.trim(), duration: 5 })
    });
    await pollJob(data.job_id);
    pollTimer = window.setInterval(() => pollJob(data.job_id), 3000);
  } catch (error) {
    setStatus("offline", "无法开始生成", error.message);
    generateButton.disabled = false;
  }
}

generateButton.addEventListener("click", generateClip);
checkH3();
