"use client";

import type { TodoItem as TodoItemType } from "@/lib/todoClient";
import styles from "./styles.css";
import CheckboxWithLabel from "../Checkbox";
import { useState } from "react";

export default function TodoItem(props: TodoItemType) {
  const { date, description, completed } = props;

  const [checked, setChecked] = useState(completed);
  const handleCheck = (value: boolean) => {
    // TODO: Find out if passing setState hooks as props is an anti-pattern.
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
          {new Date(date).toDateString()} - {completed ? "true" : "false"}
        </p>
      </div>
    </div>
  );
}
