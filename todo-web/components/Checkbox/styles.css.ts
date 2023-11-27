import { style } from "@vanilla-extract/css";

const container = style({
  display: "inline-block",
  position: "relative",
  paddingLeft: 35,
  cursor: "pointer",
});

// Hide the browser's default checkbox
const checkbox = style({
  position: "absolute",
  opacity: 0,
  cursor: "pointer",
  height: 0,
  width: 0,
});

// Create a custom checkbox
const styledCheckbox = style({
  position: "absolute",
  // top and left are relative to container
  top: "-2px",
  left: 0,
  height: 25,
  width: 25,
  backgroundColor: "#eee",
  borderRadius: 25,
  selectors: {
    // On a mouse hover of any elements in our parent, set the backgroud to grey.
    [`${container}:hover input ~ &`]: { backgroundColor: "#ccc" },
    // When the checkbox is checked, add a green background
    [`${checkbox}:checked ~ &`]: { backgroundColor: "#43a047" },
    // Create the checkmark/indicator (hidden when not checked)
    "&:after": { content: "", position: "absolute", display: "none" },
    // Show the checkmark when checked
    [`${container} input:checked ~ &:after`]: { display: "block" },
    // Style the checkmark/indicator
    [`${container} &:after`]: {
      left: 9,
      top: 5,
      width: 5,
      height: 10,
      border: "solid white",
      borderWidth: "0 3px 3px 0",
      transform: "rotate(45deg)",
    },
  },
});

export default { container, checkbox, styledCheckbox };
