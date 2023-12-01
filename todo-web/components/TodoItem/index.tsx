"use client";

import type { TodoItem as TodoItemType } from "@/lib/todoClient";
import styles from "./styles.css";
import CheckboxWithLabel from "../Checkbox";
import { useState } from "react";
import { CrossButton } from "../Button";

export default function TodoItem(props: TodoItemType) {
  const { date, description, completed } = props;

  const [checked, setChecked] = useState(completed);
  const handleCheck = (value: boolean) => {
    setChecked(value);
  };

  return (
    <div className={styles.todoItem}>
      <div className={styles.checkboxContainer}>
        <CheckboxWithLabel
          label={description}
          defaultChecked={checked}
          setChecked={handleCheck}
        />
      </div>
      <div className={styles.dateContainer}>
        <p>
          {new Date(date).toLocaleDateString("en-GB", {
            day: "numeric",
            month: "short",
          })}
        </p>
      </div>
      <CrossButton onClick={() => console.log("Confirm deletion of item!")} />
    </div>
  );
}
