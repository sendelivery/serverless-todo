import { globalStyle, style } from "@vanilla-extract/css";

const table = style({
  display: "flex",
  flexDirection: "column",
});

const headingBar = style({
  display: "flex",
  flexDirection: "row",
  marginBottom: "1rem",
});

const firstHeading = style({
  flex: 3,
});

globalStyle(`${firstHeading} > h2`, {
  margin: 0,
  marginLeft: "2rem",
});

const secondHeading = style({
  flex: 1,
});

globalStyle(`${secondHeading} > h2`, {
  margin: 0,
});

const fillerBlock = style({
  width: 25,
  height: 25,
});

const items = style({});

const styles = {
  table,
  headingBar,
  firstHeading,
  secondHeading,
  fillerBlock,
  items,
};
export default styles;
