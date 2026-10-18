const pages = Array.from(document.querySelectorAll(".book-page"));
const previousButton = document.querySelector("#previousButton");
const nextButton = document.querySelector("#nextButton");
const printButton = document.querySelector("#printButton");
const pageLabel = document.querySelector("#pageLabel");
const pageDots = document.querySelector("#pageDots");

const pageNames = ["封面", "奇怪的脚印", "蓝色羽毛", "回家的路", "故事寓意", "创作过程"];
let activePage = 0;

function createDots() {
  pages.forEach((_, index) => {
    const dot = document.createElement("button");
    dot.type = "button";
    dot.className = "page-dot";
    dot.setAttribute("aria-label", `前往第 ${index + 1} 页：${pageNames[index]}`);
    dot.addEventListener("click", () => showPage(index));
    pageDots.appendChild(dot);
  });
}

function showPage(index) {
  activePage = Math.max(0, Math.min(index, pages.length - 1));
  pages.forEach((page, pageIndex) => {
    const isActive = pageIndex === activePage;
    page.hidden = !isActive;
    page.classList.toggle("is-active", isActive);
  });

  Array.from(pageDots.children).forEach((dot, dotIndex) => {
    const isActive = dotIndex === activePage;
    dot.classList.toggle("is-active", isActive);
    dot.setAttribute("aria-current", isActive ? "page" : "false");
  });

  previousButton.disabled = activePage === 0;
  nextButton.disabled = activePage === pages.length - 1;
  pageLabel.textContent = `${pageNames[activePage]} · ${activePage + 1} / ${pages.length}`;
}

previousButton.addEventListener("click", () => showPage(activePage - 1));
nextButton.addEventListener("click", () => showPage(activePage + 1));
printButton.addEventListener("click", () => window.print());

document.addEventListener("keydown", (event) => {
  if (event.key === "ArrowLeft") showPage(activePage - 1);
  if (event.key === "ArrowRight") showPage(activePage + 1);
});

createDots();
const requestedPage = Number(new URLSearchParams(window.location.search).get("page"));
showPage(Number.isInteger(requestedPage) && requestedPage >= 1 ? requestedPage - 1 : 0);
