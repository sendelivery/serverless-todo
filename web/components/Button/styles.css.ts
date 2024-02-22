import { style } from "@vanilla-extract/css";

const simpleButton = style({
  border: 0, // Remove the default border styling
  borderRadius: 25,
  width: 25,
  height: 25,
  cursor: "pointer",
  flexShrink: 0,
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  transition: "background-color 0.2s ease",
});

const unset = style({
  backgroundColor: "#f39c12", // Orange to indicate `unset`
});

const plus = style({
  backgroundColor: "#3498db",
  selectors: {
    // Create both stems required for the plus
    "&:before, &:after": {
      content: " ",
      backgroundColor: "white",
      width: 3,
      height: 16,
      position: "absolute",
    },
    "&:before": {
      transform: "rotate(90deg)",
    },
    "&:hover": {
      backgroundColor: "#2980b9",
    },
  },
});

// Create a custom X (cross) button
const cross = style({
  backgroundColor: "#ccc",
  selectors: {
    // Create both stems required for the cross
    "&:before, &:after": {
      content: " ",
      backgroundColor: "white",
      width: 3,
      height: 16,
      position: "absolute",
    },
    "&:before": {
      transform: "rotate(45deg)",
    },
    "&:after": {
      transform: "rotate(-45deg)",
    },
    "&:hover": {
      backgroundColor: "#e74c3c",
    },
  },
});

const dismiss = style({
  backgroundColor: "#00000000",
  borderRadius: 0,
  cursor: "pointer",
  transition: "background-color 0.2s ease",
  selectors: {
    // Create both stems required for the cross
    "&:before, &:after": {
      content: " ",
      backgroundColor: "#858585",
      width: 2,
      height: 16,
      position: "absolute",
    },
    "&:before": {
      transform: "rotate(45deg)",
    },
    "&:after": {
      transform: "rotate(-45deg)",
    },
    "&:hover": {
      backgroundColor: "#d9d9d966",
    },
  },
});

const disabled = style({
  backgroundColor: "#eee",
  cursor: "default",
  selectors: {
    "&:hover": { backgroundColor: "#eee" },
  },
});

const styles = { simpleButton, unset, plus, cross, dismiss, disabled };
export default styles;
