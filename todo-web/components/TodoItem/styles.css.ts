import { globalStyle, style } from "@vanilla-extract/css";

const todoItem = style({
  display: "flex",
  marginBottom: "1rem",
});

const checkboxContainer = style({
  flex: 2,
});

const dateContainer = style({
  flex: 1,
});

globalStyle(`${todoItem} > ${dateContainer} > p`, {
  margin: "0",
});

export default { todoItem, checkboxContainer, dateContainer };
