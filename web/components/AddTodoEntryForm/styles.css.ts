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
  marginLeft: "0.5rem",
});

globalStyle(`${formContainer} *`, { fontSize: "medium" });

const form = style({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
  gap: "0.5rem",
});

const textInput = style({
  height: "1.5rem",
  width: "100%",
});

const styles = { container, form, formContainer, textInput };
export default styles;
