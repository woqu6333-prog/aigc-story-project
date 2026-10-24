"use strict";

const STORAGE_KEY = "starlight-story-house-v2";

const themeCatalog = {
  courage: { label: "勇气冒险" },
  friendship: { label: "友谊成长" },
  nature: { label: "自然守护" }
};

const form = document.querySelector("#storyForm");
const nameInput = document.querySelector("#heroName");
const ageInput = document.querySelector("#heroAge");
const interestInput = document.querySelector("#heroInterest");
const settingInput = document.querySelector("#storySetting");
const plotIdeaInput = document.querySelector("#plotIdea");
const voiceButton = document.querySelector("#voiceButton");
const voiceButtonLabel = document.querySelector("#voiceButtonLabel");
const emptyState = document.querySelector("#emptyState");
const storyResult = document.querySelector("#storyResult");
const storyTitle = document.querySelector("#storyTitle");
const storyMeta = document.querySelector("#storyMeta");
const storyBody = document.querySelector("#storyBody");
const storyMoral = document.querySelector("#storyMoral");
const storyThemeLabel = document.querySelector("#storyThemeLabel");
const storySourceNote = document.querySelector("#storySourceNote");
const generateButton = document.querySelector("#generateButton");
const generateButtonLabel = document.querySelector("#generateButtonLabel");
const polishButton = document.querySelector("#polishButton");
const regenerateButton = document.querySelector("#regenerateButton");
const copyButton = document.querySelector("#copyButton");
const downloadButton = document.querySelector("#downloadButton");
const generationStatus = document.querySelector("#generationStatus");
const generationMode = document.querySelector("#generationMode");
const generationModeDetail = document.querySelector("#generationModeDetail");
const toast = document.querySelector("#toast");

let currentStory = null;
let apiReady = false;
let apiModel = "";
let toastTimer = null;
let busy = false;

function pick(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function selectedTheme() {
  return form.elements.theme.value;
}

function currentProfile() {
  return {
    name: nameInput.value.trim(),
    age: Number(ageInput.value),
    interest: interestInput.value.trim(),
    setting: settingInput.value,
    plot_idea: plotIdeaInput.value.trim(),
    theme: selectedTheme(),
    story_length: "短篇",
    target_age: Number(ageInput.value),
    strategy: "role_constraints"
  };
}

function setFieldError(input, message) {
  const error = document.querySelector(`#${input.id}Error`);
  input.setAttribute("aria-invalid", message ? "true" : "false");
  if (error) error.textContent = message;
}

function validateForm() {
  const profile = currentProfile();
  let valid = true;

  setFieldError(nameInput, "");
  setFieldError(ageInput, "");
  setFieldError(interestInput, "");
  setFieldError(plotIdeaInput, "");

  if (!profile.name) {
    setFieldError(nameInput, "请填写主角名字");
    valid = false;
  } else if (profile.name.length > 12) {
    setFieldError(nameInput, "名字不能超过12个字符");
    valid = false;
  }

  if (!Number.isInteger(profile.age) || profile.age < 3 || profile.age > 12) {
    setFieldError(ageInput, "请输入3–12岁的整数");
    valid = false;
  }

  if (!profile.interest) {
    setFieldError(interestInput, "请填写一个兴趣");
    valid = false;
  } else if (profile.interest.length > 20) {
    setFieldError(interestInput, "兴趣不能超过20个字符");
    valid = false;
  }

  if (profile.plot_idea.length > 500) {
    setFieldError(plotIdeaInput, "剧情设想不能超过500个字符");
    valid = false;
  }

  if (!valid) {
    form.querySelector('[aria-invalid="true"]')?.focus();
    showToast("请先补全创作卡片中的信息");
  }
  return valid;
}

function ageReadingLabel(age) {
  if (age <= 5) return "亲子共读";
  if (age <= 8) return "自主阅读入门";
  return "成长阅读";
}

function createOfflineStory(profile) {
  const moonClues = ["一枚沾着露水的羽毛", "一串绕过蘑菇的小脚印", "一阵从树洞里传来的轻响"];
  const helpers = ["戴圆眼镜的蓝知更鸟", "抱着松果的小刺猬", "尾巴像蒲公英的小狐狸"];
  const clue = pick(moonClues);
  const helper = pick(helpers);

  const stories = {
    courage: {
      title: `${profile.name}和藏在月光里的线索`,
      sections: [
        {
          heading: "森林寄来的邀请",
          text: `雨停后，${profile.setting}亮起一层银光。${profile.age}岁的${profile.name}在小路边发现了${clue}。${profile.name}虽然有点紧张，却没有急着转身，而是想起自己研究${profile.interest}时最常做的事：先观察，再猜答案。`
        },
        {
          heading: "让知识照亮小路",
          text: `${helper}正为找不到家而着急。${profile.name}蹲下来比对痕迹，又把关于${profile.interest}的知识变成一个小办法。零散的线索慢慢连在一起，原本黑漆漆的岔路，也不再像刚才那样吓人了。`
        },
        {
          heading: "害怕也可以向前",
          text: `他们沿着线索找到了正确方向。月光落在回家的路上，${profile.name}终于明白：勇敢不是假装什么都不怕，而是愿意看清困难、想出办法，再认真迈出下一步。`
        }
      ],
      moral: "真正的勇气，是在认真观察和思考之后，依然愿意行动。"
    },
    friendship: {
      title: `${profile.name}和两种不一样的好办法`,
      sections: [
        {
          heading: "不合拍的新伙伴",
          text: `${profile.age}岁的${profile.name}来到${profile.setting}准备庆典，并和${helper}分到一组。${profile.name}喜欢用${profile.interest}寻找灵感，伙伴却总要安静地想很久。两个人第一次合作时，谁也跟不上谁的节奏。`
        },
        {
          heading: "先听完对方的话",
          text: `一阵风吹乱了大家的准备。${profile.name}正想独自解决，忽然注意到伙伴一直盯着${clue}。这一次，${profile.name}没有抢着开口，而是先问：“你发现了什么？”一个被忽略的办法，就这样出现了。`
        },
        {
          heading: "拼在一起的答案",
          text: `${profile.name}把${profile.interest}带来的点子和伙伴的发现合在一起，终于完成了任务。他们并没有变得一模一样，却学会了在不同的想法之间，为彼此留出认真倾听的位置。`
        }
      ],
      moral: "真正的合作不是想法相同，而是愿意倾听并让不同的优点一起发光。"
    },
    nature: {
      title: `${profile.name}和会回答的绿色回声`,
      sections: [
        {
          heading: "不再唱歌的小路",
          text: `${profile.name}走进${profile.setting}时，发现风里少了往日的声音。${clue}躺在被包装纸挡住的草丛旁，${helper}小声说，最近连回家的路都变得乱糟糟了。`
        },
        {
          heading: "从一件小事开始",
          text: `${profile.name}没有等待魔法，而是用研究${profile.interest}时学会的分类办法，把能回收和不能回收的东西分开，又画出简单的提示。看见行动真的有效，越来越多的小动物也加入进来。`
        },
        {
          heading: "森林重新有了声音",
          text: `傍晚，干净的小路重新露出来，风穿过树叶，像在回答每一个弯腰捡起垃圾的人。${profile.name}知道，一次行动也许很小，却能邀请更多人一起照顾共同的家。`
        }
      ],
      moral: "保护自然从身边的小事开始，每一个行动都可能带来新的同行者。"
    }
  };

  if (profile.plot_idea) {
    const themeLesson = {
      courage: "把害怕变成一次认真尝试",
      friendship: "先听见伙伴的想法再一起行动",
      nature: "从自己能做到的小事开始守护环境"
    }[profile.theme];
    return {
      title: `${profile.name}的三步行动计划`,
      sections: [
        {
          heading: "事情为什么发生",
          text: `故事从这个设想开始：“${profile.plot_idea}”${profile.name}没有立刻冲上去，而是先说清楚自己要解决的具体问题，并观察${profile.setting}里已经出现的线索。`
        },
        {
          heading: "第一次办法没有成功",
          text: `${profile.name}试着用自己对${profile.interest}的了解解决问题，可第一次尝试忽略了一个关键条件，因此没有成功。${profile.name}停下来重新比较线索，也认真听完伙伴的发现，终于知道刚才错在哪里。`
        },
        {
          heading: "线索带来真正的答案",
          text: `${profile.name}把前两幕已经出现的线索重新组合，换了一个更安全、更照顾大家的办法，问题终于被解决。经历这件事后，${profile.name}学会了${themeLesson}。`
        }
      ],
      moral: `好的答案来自前面留下的线索；${themeLesson}。`,
      ...profile,
      source: "offline",
      createdAt: new Date().toISOString(),
      rawStory: null,
      generationMeta: null
    };
  }

  return {
    ...stories[profile.theme],
    ...profile,
    source: "offline",
    createdAt: new Date().toISOString(),
    rawStory: null,
    generationMeta: null
  };
}

function normalizeApiStory(rawStory, profile, source, meta) {
  return {
    title: rawStory.title,
    sections: rawStory.scenes.map((scene) => ({
      heading: scene.description,
      text: scene.text,
      mood: scene.mood,
      visualPrompt: scene.visual_prompt
    })),
    moral: rawStory.moral,
    characters: rawStory.characters,
    ...profile,
    source,
    createdAt: new Date().toISOString(),
    rawStory,
    generationMeta: meta
  };
}

async function requestJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await response.json().catch(() => ({ message: "服务返回了无法解析的内容" }));
  if (!response.ok || !data.ok) throw new Error(data.message || `请求失败：${response.status}`);
  return data;
}

async function generateStory() {
  if (busy || !validateForm()) return;
  const profile = currentProfile();
  setBusy(true, apiReady ? "AI正在创作并校验……" : "正在生成离线示例……");

  try {
    if (apiReady) {
      const data = await requestJson("api/story", profile);
      currentStory = normalizeApiStory(data.story, profile, "api", data.meta);
      showToast("AI故事已生成，并通过结构校验");
    } else {
      currentStory = createOfflineStory(profile);
      showToast("已生成离线演示故事");
    }
  } catch (error) {
    currentStory = createOfflineStory(profile);
    showToast(`API暂时不可用，已切换离线演示：${error.message}`);
  } finally {
    renderStory(currentStory);
    saveState();
    setBusy(false);
  }
}

async function polishStory() {
  if (busy || !apiReady || !currentStory?.rawStory) return;
  setBusy(true, "儿童文学编辑正在二次润色……");
  try {
    const profile = currentProfile();
    const data = await requestJson("api/polish", { ...profile, story: currentStory.rawStory });
    currentStory = normalizeApiStory(data.story, profile, "api-polished", data.meta);
    renderStory(currentStory);
    saveState();
    showToast("润色完成，故事结构已再次校验");
  } catch (error) {
    showToast(`润色失败，已保留原故事：${error.message}`);
  } finally {
    setBusy(false);
  }
}

function setBusy(nextBusy, label = "") {
  busy = nextBusy;
  generateButton.disabled = nextBusy;
  regenerateButton.disabled = nextBusy;
  polishButton.disabled = nextBusy || !apiReady || !currentStory?.rawStory;
  generateButtonLabel.textContent = nextBusy ? label : "生成结构化故事";
}

function renderStory(story) {
  document.documentElement.dataset.theme = story.theme;
  storyTitle.textContent = story.title;
  storyThemeLabel.textContent = `${themeCatalog[story.theme].label} · ${sourceLabel(story.source)}`;
  storyMoral.textContent = story.moral;

  const metaItems = [
    `主角：${story.name}`,
    `${story.age}岁`,
    `兴趣：${story.interest}`,
    `场景：${story.setting}`,
    ageReadingLabel(story.age)
  ];
  if (story.plot_idea) metaItems.push("已采用自定义剧情");
  storyMeta.replaceChildren(...metaItems.map(createMetaChip));
  storySourceNote.textContent = sourceDescription(story);

  const sections = story.sections.map((section, index) => {
    const wrapper = document.createElement("section");
    const heading = document.createElement("h3");
    const paragraph = document.createElement("p");
    heading.textContent = `${String(index + 1).padStart(2, "0")} · ${section.heading}`;
    paragraph.textContent = section.text;
    wrapper.append(heading, paragraph);
    return wrapper;
  });
  storyBody.replaceChildren(...sections);

  emptyState.hidden = true;
  storyResult.hidden = false;
  polishButton.disabled = !apiReady || !story.rawStory;
  storyResult.scrollIntoView({ behavior: "smooth", block: "start" });
}

function sourceLabel(source) {
  if (source === "api-polished") return "AI润色版";
  if (source === "api") return "真实API";
  return "离线演示";
}

function sourceDescription(story) {
  if (story.source === "offline") {
    return "当前显示离线演示模板，并非大模型实时生成。请通过 scripts/run_app.py 启动网站并配置 .env，即可使用真实API。";
  }
  const meta = story.generationMeta || {};
  const time = Number.isFinite(meta.elapsed_seconds) ? `，耗时 ${meta.elapsed_seconds} 秒` : "";
  if (story.source === "api-polished") {
    return `真实API二次润色结果${time}；润色后已重新通过JSON结构、场景编号和兴趣关联校验。`;
  }
  return `真实API生成结果，Prompt策略：${meta.strategy || "role_constraints"}${time}；已通过严格JSON校验。`;
}

function createMetaChip(text) {
  const chip = document.createElement("span");
  chip.textContent = text;
  return chip;
}

function storyAsPlainText() {
  if (!currentStory) return "";
  const paragraphs = currentStory.sections
    .map((section) => `${section.heading}\n${section.text}`)
    .join("\n\n");
  return [
    currentStory.title,
    `主题：${themeCatalog[currentStory.theme].label}`,
    `主角：${currentStory.name}（${currentStory.age}岁）`,
    `兴趣：${currentStory.interest}`,
    `场景：${currentStory.setting}`,
    `来源：${sourceLabel(currentStory.source)}`,
    "",
    paragraphs,
    "",
    `故事寓意：${currentStory.moral}`,
    "",
    "—— 星光故事屋"
  ].join("\n");
}

async function copyStory() {
  if (!currentStory) return;
  const text = storyAsPlainText();
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const temporary = document.createElement("textarea");
    temporary.value = text;
    temporary.style.position = "fixed";
    temporary.style.opacity = "0";
    document.body.appendChild(temporary);
    temporary.select();
    document.execCommand("copy");
    temporary.remove();
  }
  showToast("故事已经复制到剪贴板");
}

function downloadStory() {
  if (!currentStory) return;
  const content = currentStory.rawStory
    ? JSON.stringify(currentStory.rawStory, null, 2)
    : storyAsPlainText();
  const extension = currentStory.rawStory ? "json" : "txt";
  const mime = currentStory.rawStory ? "application/json" : "text/plain";
  const blob = new Blob([content], { type: `${mime};charset=utf-8` });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const safeTitle = currentStory.title.replace(/[\\/:*?"<>|]/g, "-");
  link.href = url;
  link.download = `${safeTitle}.${extension}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  showToast(`故事${extension.toUpperCase()}已经下载`);
}

function showToast(message) {
  window.clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.add("is-visible");
  toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 3200);
}

function setGenerationMode(state, title, detail) {
  generationStatus.dataset.state = state;
  generationMode.textContent = title;
  generationModeDetail.textContent = detail;
}

async function checkApiStatus() {
  if (window.location.protocol === "file:") {
    setGenerationMode("offline", "离线演示模式", "当前直接打开HTML；启动本地Python服务后可调用真实API");
    return;
  }

  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), 2500);
  try {
    const response = await fetch("api/health", { cache: "no-store", signal: controller.signal });
    const data = await response.json();
    apiReady = Boolean(response.ok && data.api_configured);
    apiModel = data.model || "";
    if (apiReady) {
      setGenerationMode("api", "真实API模式", `已连接 ${apiModel}，支持结构化生成与二次润色`);
    } else {
      setGenerationMode("offline", "离线演示模式", "本地服务已启动，但.env尚未配置API");
    }
  } catch {
    apiReady = false;
    setGenerationMode("offline", "离线演示模式", "当前为静态网页，使用内置示例且不产生API费用");
  } finally {
    window.clearTimeout(timer);
    polishButton.disabled = !apiReady || !currentStory?.rawStory;
  }
}

function saveState() {
  const state = {
    form: {
      name: nameInput.value.trim(),
      age: ageInput.value,
      interest: interestInput.value.trim(),
      setting: settingInput.value,
      plot_idea: plotIdeaInput.value.trim(),
      theme: selectedTheme()
    },
    story: currentStory
  };
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // 隐私模式可能禁用本地存储，不影响生成流程。
  }
}

function restoreState() {
  try {
    const state = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (!state?.form) return;
    nameInput.value = state.form.name ?? "";
    ageInput.value = state.form.age ?? "";
    interestInput.value = state.form.interest ?? "";
    settingInput.value = state.form.setting || "月光森林";
    plotIdeaInput.value = state.form.plot_idea || "";
    const themeInput = form.querySelector(`input[name="theme"][value="${state.form.theme}"]`);
    if (themeInput) themeInput.checked = true;
    document.documentElement.dataset.theme = state.form.theme || "courage";
    if (state.story?.title && Array.isArray(state.story.sections)) {
      currentStory = state.story;
      renderStory(currentStory);
    }
  } catch {
    localStorage.removeItem(STORAGE_KEY);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  generateStory();
});

form.addEventListener("input", (event) => {
  if (event.target.matches("input:not([type='radio']), textarea")) setFieldError(event.target, "");
});

form.addEventListener("change", (event) => {
  if (event.target.name === "theme") document.documentElement.dataset.theme = event.target.value;
  saveState();
});

regenerateButton.addEventListener("click", generateStory);
polishButton.addEventListener("click", polishStory);
copyButton.addEventListener("click", copyStory);
downloadButton.addEventListener("click", downloadStory);

function startVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showToast("当前浏览器不支持语音识别，请直接输入剧情");
    return;
  }
  const recognition = new SpeechRecognition();
  recognition.lang = "zh-CN";
  recognition.interimResults = true;
  recognition.continuous = false;
  const original = plotIdeaInput.value.trim();
  voiceButton.disabled = true;
  voiceButton.classList.add("is-listening");
  voiceButtonLabel.textContent = "正在听……";
  recognition.onresult = (event) => {
    const transcript = Array.from(event.results).map((result) => result[0].transcript).join("");
    plotIdeaInput.value = [original, transcript].filter(Boolean).join(original ? "，" : "").slice(0, 500);
  };
  recognition.onerror = (event) => showToast(`语音识别没有完成：${event.error}`);
  recognition.onend = () => {
    voiceButton.disabled = false;
    voiceButton.classList.remove("is-listening");
    voiceButtonLabel.textContent = "说出剧情";
    saveState();
  };
  recognition.start();
}

voiceButton.addEventListener("click", startVoiceInput);

restoreState();
checkApiStatus();
