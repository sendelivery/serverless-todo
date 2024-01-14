"use client";

import { useRef, useState, type ChangeEvent } from "react";
import { type TodoEntry } from "@/lib/todoClient";
import styles from "./styles.css";
import { SimpleButton } from "../Button";
import { createEntry } from "@/app/actions";

export type AddTodoEntryFormProps = {
  addEntry: (newEntry: TodoEntry) => void;
};

export default function AddTodoEntryForm({ addEntry }: AddTodoEntryFormProps) {
  const formRef = useRef<HTMLFormElement>(null);
  const [disabled, setDisabled] = useState(true);

  function handleDescriptionChange(e: ChangeEvent<HTMLInputElement>) {
    // Disallow submitting whitespace.
    const text = e.target.value.trim();
    setDisabled(text ? false : true);
  }

  function formAction(formData: FormData) {
    formRef.current!.reset();
    setDisabled(true);
    createEntry(formData).then((todoEntry) => {
      addEntry(todoEntry);
    });
  }

  return (
    <div className={styles.container}>
      <form action={formAction} ref={formRef} className={styles.form}>
        <input
          name="description"
          className={styles.textInput}
          onChange={handleDescriptionChange}
          placeholder="Write a short description to add to your Todo list"
          autoComplete="off"
        />
        <SimpleButton simpleStyle="plus" disabled={disabled} type="submit" />
      </form>
    </div>
  );
}
