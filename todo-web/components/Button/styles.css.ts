import { style } from "@vanilla-extract/css";

const button = style({
  backgroundColor: "#43a047",
});

// Create a custom X (cross) button
const crossButton = style({
  borderRadius: 25,
  width: 25,
  height: 25,
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

export default { button, crossButton };
