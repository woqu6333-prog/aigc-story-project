"use strict";

const STORAGE_KEY = "starlight-story-house-v1";

const themeCatalog = {
  courage: {
    label: "勇气冒险",
    create({ name, age, interest }) {
      const places = ["会移动的月光森林", "漂浮在云海上的灯塔岛", "每到夜里就会发光的山谷"];
      const companions = ["一只尾巴像蒲公英的小狐狸", "一只戴圆眼镜的蓝知更鸟", "一个装着微小星光的纸灯笼"];
      const obstacles = ["一座只回应真心话的石门", "一条被浓雾藏起来的小路", "一阵把声音都吹走的怪风"];
      const place = pick(places);
      const companion = pick(companions);
      const obstacle = pick(obstacles);

      return {
        title: `${name}和不肯熄灭的星光`,
        sections: [
          {
            heading: "一封月光来信",
            text: `${age}岁的${name}最喜欢${interest}。一天傍晚，窗台上落下一封银色的信，信上写着：“${place}失去了一颗重要的星星，需要一位愿意出发的小小旅人。”${name}心里有一点紧张，却还是把最喜欢的${interest}图案徽章别在胸前，轻轻推开了那扇月光做成的门。`
          },
          {
            heading: "看不清的前路",
            text: `门后站着${companion}。它告诉${name}，只有穿过${obstacle}，才能把星星送回夜空。走到半路，四周突然变得安静又黑暗。${name}很想回家，但想起还有许多孩子在等星光照亮窗边，便握紧徽章说：“害怕也没关系，我可以一步一步来。”`
          },
          {
            heading: "勇气发出声音",
            text: `${name}没有假装自己什么都不怕，而是把担心说给同伴听。他们一起观察风的方向，又用关于${interest}的知识想出办法。每向前一步，胸前的徽章就亮一点。最后，${obstacle}不再可怕，它变成了一条闪着金光的路，把他们送到了山顶。`
          },
          {
            heading: "回到窗边的星星",
            text: `${name}把星星轻轻放回天空。整个${place}重新亮了起来，连远处的屋顶也铺上温柔的银光。回家以后，窗台上多了一颗小小的亮点。每当${name}遇到困难，它就像在说：“勇敢不是从不害怕，而是害怕的时候，仍愿意试一试。”`
          }
        ],
        moral: "真正的勇气不是没有害怕，而是承认害怕以后，仍然愿意认真地迈出下一步。"
      };
    }
  },
  friendship: {
    label: "友谊成长",
    create({ name, age, interest }) {
      const friends = ["慢吞吞的小刺猬团团", "说话像唱歌的小鹿米米", "总把帽子戴反的小熊布丁"];
      const events = ["森林分享节", "月亮湖野餐会", "会发光的风筝比赛"];
      const problems = ["装饰会场的彩带被风吹散了", "大家准备的点心不小心打翻了", "比赛用的风筝线全缠在了一起"];
      const friend = pick(friends);
      const event = pick(events);
      const problem = pick(problems);

      return {
        title: `${name}和装满笑声的口袋`,
        sections: [
          {
            heading: "特别的新同桌",
            text: `${age}岁的${name}喜欢${interest}，也喜欢把新发现画在小卡片上。准备${event}的那天，老师安排${name}和${friend}一起工作。可是他们一个做事快，一个想得慢，刚开始总是碰不到同一个节拍。两个人都觉得，也许独自完成会更容易。`
          },
          {
            heading: "一场小小的意外",
            text: `就在活动快要开始时，${problem}。大家急得团团转。${name}本想马上按照自己的办法解决，却发现${friend}一直安静地观察。${name}停下来问：“你是不是想到了什么？”朋友点点头，说出了一个谁也没有注意到的好主意。`
          },
          {
            heading: "两种办法拼在一起",
            text: `${name}把自己熟悉的${interest}用进方案里，${friend}则负责最需要耐心的部分。他们不再抢着证明谁的办法更好，而是认真听完对方的话。一个人的点子像一块拼图，两个人的点子合起来，竟变成了一幅完整又漂亮的图画。`
          },
          {
            heading: "装满笑声的口袋",
            text: `${event}顺利开始了。回家的路上，${friend}送给${name}一只纸做的小口袋，说里面装着今天的笑声。${name}也送出一张画着两颗星星的卡片。从那以后，他们仍然有不同的想法，却学会了先倾听、再商量，因为好朋友不必一模一样。`
          }
        ],
        moral: "友谊不是要求彼此完全相同，而是愿意倾听、分享，并让不同的优点一起发光。"
      };
    }
  },
  nature: {
    label: "自然守护",
    create({ name, age, interest }) {
      const places = ["会唱歌的小河", "藏着彩色种子的森林", "海风总带着咸味的贝壳湾"];
      const messengers = ["一片会说悄悄话的绿叶", "一只脚上沾着露珠的蜗牛", "一颗从泥土里探出头的小种子"];
      const troubles = ["水面漂来了许多包装纸", "小动物们找不到干净的饮水", "花草因为垃圾挡住阳光而低下了头"];
      const place = pick(places);
      const messenger = pick(messengers);
      const trouble = pick(troubles);

      return {
        title: `${name}和绿色回声计划`,
        sections: [
          {
            heading: "来自大自然的邀请",
            text: `${age}岁的${name}正在研究最喜欢的${interest}，忽然听见窗外有人轻轻敲玻璃。原来是${messenger}，它从${place}赶来求助。那里过去清亮又热闹，如今却遇到了麻烦：${trouble}。${name}背上水壶和布袋，决定亲自去看一看。`
          },
          {
            heading: "不是魔法的问题",
            text: `到了${place}，${name}发现没有哪个魔法能让所有垃圾瞬间消失。于是，${name}先把能回收的东西分类，再请小动物们记录垃圾来自哪里。关于${interest}的经验还带来了新点子：把旧材料改造成醒目的提示牌，让经过的人都能看懂。`
          },
          {
            heading: "一件小事带来的改变",
            text: `一开始，只有${name}和${messenger}在行动。后来，松鼠送来了旧纸箱，小鸟负责把消息传远，路过的人也弯腰捡起脚边的瓶盖。大家约定少用一次性物品，并把垃圾带回正确的地方。一天又一天，清洁的范围越来越大。`
          },
          {
            heading: "绿色的回声",
            text: `不久，${place}重新有了清澈的颜色，花草抬起头，小动物也回到了熟悉的家。风吹过树梢时，叶子沙沙作响，像在重复${name}说过的话：“保护自然不一定要做惊天动地的大事，每一个认真完成的小行动，都会被世界听见。”`
          }
        ],
        moral: "爱护环境从身边的小事开始；一个人的行动很小，却能邀请更多人一起改变。"
      };
    }
  }
};

const form = document.querySelector("#storyForm");
const nameInput = document.querySelector("#heroName");
const ageInput = document.querySelector("#heroAge");
const interestInput = document.querySelector("#heroInterest");
const emptyState = document.querySelector("#emptyState");
const storyResult = document.querySelector("#storyResult");
const storyTitle = document.querySelector("#storyTitle");
const storyMeta = document.querySelector("#storyMeta");
const storyBody = document.querySelector("#storyBody");
const storyMoral = document.querySelector("#storyMoral");
const storyThemeLabel = document.querySelector("#storyThemeLabel");
const regenerateButton = document.querySelector("#regenerateButton");
const copyButton = document.querySelector("#copyButton");
const downloadButton = document.querySelector("#downloadButton");
const toast = document.querySelector("#toast");

let currentStory = null;
let toastTimer = null;

function pick(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function selectedTheme() {
  return form.elements.theme.value;
}

function setFieldError(input, message) {
  const error = document.querySelector(`#${input.id}Error`);
  input.setAttribute("aria-invalid", message ? "true" : "false");
  if (error) error.textContent = message;
}

function validateForm() {
  const name = nameInput.value.trim();
  const age = Number(ageInput.value);
  const interest = interestInput.value.trim();
  let valid = true;

  setFieldError(nameInput, "");
  setFieldError(ageInput, "");
  setFieldError(interestInput, "");

  if (!name) {
    setFieldError(nameInput, "请填写主角名字");
    valid = false;
  } else if (name.length > 12) {
    setFieldError(nameInput, "名字不能超过12个字符");
    valid = false;
  }

  if (!Number.isInteger(age) || age < 3 || age > 12) {
    setFieldError(ageInput, "请输入3–12岁的整数");
    valid = false;
  }

  if (!interest) {
    setFieldError(interestInput, "请填写一个兴趣");
    valid = false;
  } else if (interest.length > 20) {
    setFieldError(interestInput, "兴趣不能超过20个字符");
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

function generateStory() {
  if (!validateForm()) return;

  const profile = {
    name: nameInput.value.trim(),
    age: Number(ageInput.value),
    interest: interestInput.value.trim(),
    theme: selectedTheme()
  };

  const generated = themeCatalog[profile.theme].create(profile);
  currentStory = { ...generated, ...profile, createdAt: new Date().toISOString() };
  renderStory(currentStory);
  saveState();
}

function renderStory(story) {
  document.documentElement.dataset.theme = story.theme;
  storyTitle.textContent = story.title;
  storyThemeLabel.textContent = themeCatalog[story.theme].label;
  storyMoral.textContent = story.moral;

  const metaItems = [
    `主角：${story.name}`,
    `${story.age}岁`,
    `兴趣：${story.interest}`,
    ageReadingLabel(story.age)
  ];
  storyMeta.replaceChildren(...metaItems.map(createMetaChip));

  const sections = story.sections.map((section) => {
    const wrapper = document.createElement("section");
    const heading = document.createElement("h3");
    const paragraph = document.createElement("p");
    heading.textContent = section.heading;
    paragraph.textContent = section.text;
    wrapper.append(heading, paragraph);
    return wrapper;
  });
  storyBody.replaceChildren(...sections);

  emptyState.hidden = true;
  storyResult.hidden = false;
  storyResult.scrollIntoView({ behavior: "smooth", block: "start" });
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
  const blob = new Blob([storyAsPlainText()], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const safeTitle = currentStory.title.replace(/[\\/:*?"<>|]/g, "-");
  link.href = url;
  link.download = `${safeTitle}.txt`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  showToast("故事文本已经下载");
}

function showToast(message) {
  window.clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.add("is-visible");
  toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 2200);
}

function saveState() {
  const state = {
    form: {
      name: nameInput.value.trim(),
      age: ageInput.value,
      interest: interestInput.value.trim(),
      theme: selectedTheme()
    },
    story: currentStory
  };

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // 部分隐私浏览器可能禁用本地存储，不影响页面核心功能。
  }
}

function restoreState() {
  try {
    const state = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (!state?.form) return;

    nameInput.value = state.form.name ?? "";
    ageInput.value = state.form.age ?? "";
    interestInput.value = state.form.interest ?? "";

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
  if (event.target.matches("input:not([type='radio'])")) {
    setFieldError(event.target, "");
  }
});

form.addEventListener("change", (event) => {
  if (event.target.name === "theme") {
    document.documentElement.dataset.theme = event.target.value;
    saveState();
  }
});

regenerateButton.addEventListener("click", generateStory);
copyButton.addEventListener("click", copyStory);
downloadButton.addEventListener("click", downloadStory);

restoreState();
