"use client";

import { useEffect, useState } from "react";
import { SimpleButton } from "../../Button";
import styles from "./styles.css";

const FADE_ANIMATION_DURATION = 200;

export type ToastProps = {
  message: string;
  level: "info" | "error";
  lifespan: number | "inf";
  remove: () => void;
};

export default function Toast(props: ToastProps) {
  const containerLevel: "infoStyle" | "errorStyle" = `${props.level}Style`;
  const iconLevel: "infoIcon" | "errorIcon" = `${props.level}Icon`;

  const [fade, setFade] = useState<"fadeIn" | "fadeOut">("fadeIn");
  useEffect(() => {
    if (fade === "fadeIn") {
      if (props.lifespan === "inf") {
        return;
      }
      setTimeout(() => setFade("fadeOut"), props.lifespan);
    } else {
      setTimeout(props.remove, FADE_ANIMATION_DURATION);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fade]);

  return (
    <div
      className={`${styles.container} ${styles[containerLevel]} ${styles[fade]}`}
    >
      <div className={`${styles.icon} ${styles[iconLevel]}`}></div>
      <div className={styles.messageContainer} lang="en">
        <p>{props.message}</p>
      </div>
      <SimpleButton simpleStyle="dismiss" onClick={() => setFade("fadeOut")} />
    </div>
  );
}
