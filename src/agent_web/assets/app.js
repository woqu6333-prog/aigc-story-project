const plan=[
  ["retrieve_materials","从作业5素材库召回模板、人物、场景、插画和音效"],
  ["write_structured_story","根据最新状态生成三幕JSON故事"],
  ["illustrate_scenes","固定人物描述，生成3张场景插画"],
  ["synthesize_narration","调用Edge TTS生成中文旁白MP3"],
  ["compose_story_video","调用FFmpeg合成最终MP4"]
];
const cases={
  "case-01-space":{label:"案例1 · 人物干预",before:"男孩阿川 · 太空",after:"女孩小星 · 太空"},
  "case-02-ocean":{label:"案例2 · 场景干预",before:"女孩小星 · 月光森林",after:"女孩小星 · 海底珊瑚城"}
};
function renderPlan(){const list=document.querySelector("#planList");list.replaceChildren();for(const [name,desc] of plan){const item=document.createElement("li");item.innerHTML=`<i></i><div><strong>${name}</strong><p>${desc}</p></div>`;list.append(item)}document.querySelector("#planStatus").textContent="5步 · 待执行"}
document.querySelector("#planButton").addEventListener("click",renderPlan);
document.querySelector("#interveneButton").addEventListener("click",()=>{renderPlan();const text=document.querySelector("#interventionInput").value.trim()||"未填写修改";document.querySelector("#stateChange").hidden=false;document.querySelector("#changeText").textContent=`${text}。人物与场景状态已更新，旧的故事和媒体成果已标记为失效。`;document.querySelector("#planStatus").textContent="已重排 · 等待执行"});
async function loadCase(id){document.querySelectorAll("[data-case]").forEach(button=>button.classList.toggle("active",button.dataset.case===id));const state=await fetch(`data/${id}.json`).then(r=>r.json());const info=cases[id];document.querySelector("#caseVideo").src=`media/${id}/story-video.mp4`;document.querySelector("#duration").textContent=`${Math.round(state.artifacts.video_duration_seconds)}秒`;document.querySelector("#caseLabel").textContent=info.label;document.querySelector("#caseTitle").textContent=state.story.title;document.querySelector("#caseIdea").textContent=`原始创意：${state.idea}`;document.querySelector("#caseBefore").textContent=info.before;document.querySelector("#caseAfter").textContent=info.after;const scenes=document.querySelector("#sceneList");scenes.replaceChildren();for(const scene of state.story.scenes){const li=document.createElement("li");li.textContent=`${scene.title}：${scene.content.slice(0,34)}……`;scenes.append(li)}}
document.querySelectorAll("[data-case]").forEach(button=>button.addEventListener("click",()=>loadCase(button.dataset.case)));
loadCase("case-01-space").catch(error=>{document.querySelector("#caseTitle").textContent=`案例载入失败：${error.message}`});
