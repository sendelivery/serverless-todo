"use client";

import styles from "./styles.css";

export type ButtonWithTextProps = {
  text: string;
  onClick: () => void;
};

export function ButtonWithText(props: ButtonWithTextProps) {
  return (
    <div>
      <button type="button" onClick={props.onClick}>
        {props.text}
      </button>
    </div>
  );
}

export type CrossButtonProps = {
  onClick?: () => void;
};

export function CrossButton(props: CrossButtonProps) {
  return <div className={styles.crossButton} onClick={props.onClick}></div>;
}
