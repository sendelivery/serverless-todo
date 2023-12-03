import { style } from "@vanilla-extract/css";

const simpleButton = style({
  border: 0, // Remove the default border styling
  borderRadius: 25,
  width: 25,
  height: 25,
  cursor: "pointer",
});

const unset = style({
  backgroundColor: "#f39c12", // Orange to indicate `unset`
});

const plus = style({
  backgroundColor: "#3498db",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
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
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
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

const disabled = style({
  backgroundColor: "#eee",
  cursor: "default",
  selectors: {
    "&:hover": { backgroundColor: "#eee" },
  },
});

export default { simpleButton, unset, plus, cross, disabled };
