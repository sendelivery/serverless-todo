import { ReactNode } from "react";
import styles from "./styles.css";

export default function Toaster({ children }: { children: ReactNode }) {
  return <div className={styles.container}>{children}</div>;
}
