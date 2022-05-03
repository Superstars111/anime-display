// from https://css-tricks.com/value-bubbles-for-range-inputs/

const ratingButton = document.getElementById("ratingButton");

let sliders = [
  ratingButton,
  document.getElementById("scoreRange"),
  document.getElementById("pacingRange"),
  document.getElementById("energyRange"),
  document.getElementById("toneRange"),
  document.getElementById("fantasyRange"),
  document.getElementById("abstractionRange"),
  document.getElementById("proprietyRange")
]

const RBVAR = partial(setVariables, url, sliders, log);

ratingButton.onclick = RBVAR;

function log() {
  console.log("Values updated")
}

const allRanges = document.querySelectorAll(".range-wrap");
allRanges.forEach(wrap => {
  const range = wrap.querySelector(".slider");
  const bubble = wrap.querySelector(".bubble");

  range.addEventListener("input", () => {
    setBubble(range, bubble);
  });
  setBubble(range, bubble);
});

function setBubble(range, bubble) {
  const val = range.value;
  const min = range.min ? range.min : 0;
  const max = range.max ? range.max : 100;
  const newVal = Number(((val - min) * 100) / (max - min));
  bubble.innerHTML = Math.abs(val);

  // Sorta magic numbers based on size of the native UI thumb
  bubble.style.left = `calc(${newVal}% + (${8 - newVal * 0.15}px))`;
}
