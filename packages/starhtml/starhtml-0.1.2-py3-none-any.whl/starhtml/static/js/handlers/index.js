import persist_default from "./persist.js";
import scroll_default from "./scroll.js";
import resize_default from "./resize.js";
const persist = persist_default;
const scroll = scroll_default;
const resize = resize_default;
export {
  persist,
  persist_default as persistPlugin,
  resize,
  resize_default as resizePlugin,
  scroll,
  scroll_default as scrollPlugin
};
