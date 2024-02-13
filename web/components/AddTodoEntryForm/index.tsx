import { useRef, useState, type ChangeEvent } from "react";
import utilStyles from "@/styles/utilities.css";
import styles from "./styles.css";
import { SimpleButton } from "../Button";

export type AddTodoEntryFormProps = {
  formAction: (formData: FormData) => void;
};

export default function AddTodoEntryForm({
  formAction,
}: AddTodoEntryFormProps) {
  const formRef = useRef<HTMLFormElement>(null);
  const [disabled, setDisabled] = useState(true);

  function handleDescriptionChange(e: ChangeEvent<HTMLInputElement>) {
    // Disallow submitting whitespace.
    const text = e.target.value.trim();
    setDisabled(text ? false : true);
  }

  function handleFormAction(formData: FormData) {
    formRef.current!.reset();
    setDisabled(true);
    formAction(formData);
  }

  return (
    <div className={styles.container}>
      <h2 className={utilStyles.headingLg}>Create New Entry:</h2>
      <div className={styles.formContainer}>
        <form action={handleFormAction} ref={formRef} className={styles.form}>
          <input
            name="description"
            type="text"
            required
            className={styles.textInput}
            onChange={handleDescriptionChange}
            placeholder="Write a short description to add to your Todo list"
            autoComplete="off"
          />
          <SimpleButton simpleStyle="plus" disabled={disabled} type="submit" />
        </form>
      </div>
    </div>
  );
}
