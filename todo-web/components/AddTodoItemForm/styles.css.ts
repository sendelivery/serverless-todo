import { style } from "@vanilla-extract/css";

const form = style({
  display: "flex",
  flexDirection: "row",
  justifyContent: "center",
  width: "80%",
  height: "1.5rem",
});

const textInput = style({
  width: "60%",
});

const submitButton = style({
  width: "4rem",
});

export default { form, textInput, submitButton };
