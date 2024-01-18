import { globalStyle, style } from "@vanilla-extract/css";

const container = style({
  margin: "1.5rem",
  marginBottom: "5rem",
  display: "flex",
  flexDirection: "row",
  alignItems: "center",
});

const formContainer = style({
  flex: 1,
});

globalStyle(`${formContainer} *`, { fontSize: "medium" });

const form = style({
  display: "flex",
  flexDirection: "row",
  justifyContent: "center",
  alignItems: "center",
  gap: "0.5rem",
});

const textInput = style({
  height: "1.5rem",
  width: "85%",
});

export default { container, form, formContainer, textInput };
