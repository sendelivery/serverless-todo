import { globalStyle, style } from "@vanilla-extract/css";

const todoItem = style({
  display: "flex",
  minHeight: "25px",
});

const checkboxContainer = style({
  flex: 3,
});

const dateContainer = style({
  flex: 1,
});

globalStyle(`${todoItem} > ${dateContainer} > p`, {
  margin: "0",
});

const styles = { todoItem, checkboxContainer, dateContainer };
export default styles;
