import { style } from "@vanilla-extract/css";

const container = style({
  position: "fixed",
  width: "100%",
  top: 0,
  left: 0,
  display: "flex",
  flexDirection: "column",
  alignItems: "flex-end",
});

export default { container };
