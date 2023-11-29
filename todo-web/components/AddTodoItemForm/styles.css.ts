import { style } from "@vanilla-extract/css";

const container = style({
  margin: "2rem",
});

const form = style({
  display: "flex",
  flexDirection: "row",
  justifyContent: "center",
  height: "1.5rem",
});

const textInput = style({
  width: "60%",
});

const submitButton = style({
  width: "4rem",
});

export default { container, form, textInput, submitButton };
