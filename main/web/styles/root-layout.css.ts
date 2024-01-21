import { style } from "@vanilla-extract/css";

const container = style({
  maxWidth: "48rem",
  minWidth: "32rem",
  padding: "0 1rem",
  margin: "3rem auto 6rem",
});

const header = style({
  marginTop: "2rem",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
});

export default { container, header };
