export function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[char]));
}
export const escapeAttr = escapeHTML;
export function clamp(value, min, max) { return Math.min(max, Math.max(min, value)); }
export function normalize(value) { return String(value ?? "").normalize("NFKD").toLowerCase().replace(/[^a-z0-9]+/g," ").trim(); }
export function parseDropRate(value) {
  const raw = String(value ?? "").trim();
  if (!raw || /[{}]|#(expr|var)/i.test(raw)) return null;
  if (/always/i.test(raw)) return 1;
  const match = raw.match(/(\d+(?:[,.]\d+)?)\s*\/\s*(\d+(?:[,.]\d+)?)/);
  if (!match) return null;
  const numerator = Number(match[1].replace(/,/g, ""));
  const denominator = Number(match[2].replace(/,/g, ""));
  return Number.isFinite(numerator) && Number.isFinite(denominator) && numerator > 0 && denominator > 0 ? denominator / numerator : null;
}
export function debounce(fn, delay) {
  let timer = 0;
  return function (...args) { clearTimeout(timer); timer = setTimeout(() => fn.apply(this, args), delay); };
}
export function createTextElement(tag, text, className) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = String(text ?? "");
  return element;
}
function sanitizeHTML(html) {
  const doc = new DOMParser().parseFromString(String(html ?? ""), "text/html");
  for (const node of [...doc.body.querySelectorAll("*")]) {
    if (["SCRIPT", "STYLE", "IFRAME", "OBJECT", "EMBED", "FORM"].includes(node.tagName)) {
      node.remove();
      continue;
    }
    for (const attribute of [...node.attributes]) {
      const name = attribute.name.toLowerCase();
      const value = attribute.value.trim();
      if (name.startsWith("on") || name === "style" || name === "srcdoc") {
        node.removeAttribute(attribute.name);
        continue;
      }
      if ((name === "href" || name === "src" || name === "action") &&
          /^(?:javascript|vbscript|data):/i.test(value)) {
        node.removeAttribute(attribute.name);
      }
    }
  }
  return [...doc.body.childNodes].map(node => node.cloneNode(true));
}
export function setHTML(element, html) {
  if (!element) return element;
  element.replaceChildren(...sanitizeHTML(html));
  return element;
}
export function appendHTML(element, html) {
  if (!element) return element;
  element.append(...sanitizeHTML(html));
  return element;
}
