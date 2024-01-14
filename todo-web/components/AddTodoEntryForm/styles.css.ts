import { globalStyle, style } from "@vanilla-extract/css";

const container = style({
  margin: "2rem",
});

globalStyle(`${container} *`, { fontSize: "medium" });

const form = style({
  display: "flex",
  flexDirection: "row",
  justifyContent: "center",
  alignItems: "center",
  gap: "0.5rem",
});

const textInput = style({
  height: "1.5rem",
  width: "60%",
});

export default { container, form, textInput };
