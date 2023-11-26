import { globalStyle, style } from "@vanilla-extract/css";

const todoItem = style({
  display: "flex",
  marginBottom: "1rem",
});

globalStyle(`${todoItem} > p`, {
  margin: "0 0 0 2rem",
});

export default { todoItem };
