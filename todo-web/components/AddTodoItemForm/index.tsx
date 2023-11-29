"use client";

import type { FormEvent } from "react";
import { upsertTodoItem, type TodoItem } from "@/lib/todoClient";
import styles from "./styles.css";

export type AddTodoItemFormProps = {
  action: (item: TodoItem) => void;
};

export default function AddTodoItemForm(props: AddTodoItemFormProps) {
  function isFormValid(formData: FormData) {
    let input = formData.get("itemDescription") as string;
    input = input.trim();
    if (input === "") {
      return false;
    }
    return true;
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    // Prevent the browser from reloading the page
    e.preventDefault();

    // Access the form data and parse it into a TodoItem
    const formData = new FormData(e.currentTarget);
    e.currentTarget.reset();

    if (!isFormValid(formData)) {
      // clear form
      return;
    }

    const todoItem: TodoItem = {
      date: new Date().toISOString(),
      description: formData.get("itemDescription") as string,
      completed: false,
    };

    // TODO: Cannot use async / await in client components
    // but, this needs to be a client component because we want to be able to handle state
    // look into API routes to be able to call `upsertTodoItem(...)`
    // await upsertTodoItem(todoItem);
    props.action(todoItem);
    // clear form data
  }

  return (
    <div className={styles.container}>
      <form method="POST" onSubmit={handleSubmit} className={styles.form}>
        <input name="itemDescription" className={styles.textInput} />
        <button type="submit" className={styles.submitButton}>
          Add
        </button>
      </form>
    </div>
  );
}
