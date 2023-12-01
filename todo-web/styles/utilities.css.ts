import { style } from "@vanilla-extract/css";

const heading2Xl = style({
  fontSize: "2.5rem",
  lineHeight: "1.2",
  fontWeight: "800",
  letterSpacing: "-0.05rem",
  margin: "1rem 0",
});

const headingXl = style({
  fontSize: "2rem",
  lineHeight: "1.3",
  fontWeight: "800",
  letterSpacing: "-0.05rem",
  margin: "1rem 0",
});

const headingLg = style({
  fontSize: "1.5rem",
  lineHeight: "1.4",
  margin: "1rem 0",
});

const lightText = style({
  color: "#666",
});

export default { heading2Xl, headingXl, headingLg, lightText };
