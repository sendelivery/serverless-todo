import { style, globalStyle, keyframes } from "@vanilla-extract/css";

const fadeInAnimation = keyframes({
  "0%": { opacity: 0, translate: 10 },
  "100%": { opacity: 1, translate: 0 },
});

const fadeIn = style({
  animationName: fadeInAnimation,
  animationDuration: "0.2s",
  animationFillMode: "forwards",
});

const fadeOutAnimation = keyframes({
  "0%": { opacity: 1, translate: 0 },
  "100%": { opacity: 0, translate: 1 },
});

const fadeOut = style({
  animationName: fadeOutAnimation,
  animationDuration: "0.2s",
  animationFillMode: "forwards",
});

const container = style({
  margin: 10,
  marginBottom: 0,
  display: "flex",
  minHeight: "25px",
  width: "28rem",
  borderRadius: 5,
  padding: 6,
});

const errorStyle = style({
  border: "solid #e74c3c 1px",
  backgroundColor: "#ffecea",
});

const infoStyle = style({
  border: "solid #3498db 1px",
  backgroundColor: "#e9f2ff",
});

const icon = style({
  minWidth: 25,
  height: 25,
  borderRadius: 25,
  flexShrink: 0,
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
});

const errorIcon = style({
  backgroundColor: "#e74c3c",
  selectors: {
    "&:before": {
      content: " ",
      backgroundColor: "white",
      width: 3,
      height: 16,
      position: "absolute",
    },
    "&:after": {
      content: " ",
      backgroundColor: "#e74c3c",
      width: 3,
      height: 3,
      position: "absolute",
      marginTop: 7,
    },
  },
});

const infoIcon = style({
  backgroundColor: "#3498db",
  selectors: {
    "&:before": {
      content: " ",
      backgroundColor: "white",
      width: 3,
      height: 12,
      position: "absolute",
    },
    "&:after": {
      content: " ",
      backgroundColor: "#3498db",
      width: 3,
      height: 3,
      position: "absolute",
      marginBottom: 2,
    },
  },
});

const messageContainer = style({
  width:
    "calc(100% - 50px)" /* The size of our div, take away the icon and button widths */,
  wordBreak: "break-word",
});

globalStyle(`${container} > ${messageContainer} > p`, {
  margin: 3,
  marginLeft: 7,
});

export default {
  fadeIn,
  fadeOut,
  container,
  errorStyle,
  infoStyle,
  icon,
  errorIcon,
  infoIcon,
  messageContainer,
};
