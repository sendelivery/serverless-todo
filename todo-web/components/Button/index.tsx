import { ButtonHTMLAttributes } from "react";
import styles from "./styles.css";

export type SimpleButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  simpleStyle?: "plus" | "cross" | "unset";
};

export function SimpleButton({
  simpleStyle = "unset",
  ...buttonAttributes
}: SimpleButtonProps) {
  return (
    <button
      className={`${styles.simpleButton} ${styles[simpleStyle]} ${
        buttonAttributes.disabled && styles.disabled
      }`}
      onClick={buttonAttributes.onClick}
    ></button>
  );
}
