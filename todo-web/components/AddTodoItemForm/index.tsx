"use client";

import { useState, type ChangeEvent, type FormEvent } from "react";
import { TodoEntryInput } from "@/lib/todoClient";
import styles from "./styles.css";
import { SimpleButton } from "../Button";

export type AddTodoItemFormProps = {
  action: (item: TodoEntryInput) => void;
};

export default function AddTodoItemForm(props: AddTodoItemFormProps) {
  const [description, setDescription] = useState("");

  function handleFormChange(e: ChangeEvent<HTMLInputElement>) {
    const text = e.target.value;

    if (text) {
      setDescription(text);
      return;
    }

    setDescription("");
  }

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
    setDescription("");

    if (!isFormValid(formData)) {
      // clear form
      return;
    }

    const todoItem: TodoEntryInput = {
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
        <input
          name="itemDescription"
          className={styles.textInput}
          onChange={handleFormChange}
          placeholder="Write a short description to add to your Todo list"
          autoComplete="off"
        />
        <SimpleButton
          simpleStyle="plus"
          disabled={!description}
          type="submit"
        />
      </form>
    </div>
  );
}
