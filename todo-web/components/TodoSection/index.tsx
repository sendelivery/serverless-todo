"use client";

import { Fragment, useContext, useState } from "react";
import utilStyles from "@/styles/utilities.css";
import styles from "./styles.css";
import { type TodoEntry } from "@/lib/todoClient";
import TodoItem from "../TodoItem";
import AddTodoEntryForm from "../AddTodoEntryForm";
import { deleteEntry, postEntry } from "@/app/actions";
import { ToastQueueContext } from "../ToastQueueProvider";

type TodoSectionProps = {
  entries: TodoEntry[];
};

export default function TodoSection(props: TodoSectionProps) {
  const [entries, setEntries] = useState<TodoEntry[]>(props.entries);
  const { enqueueToast } = useContext(ToastQueueContext);

  function addEntry(formData: FormData) {
    postEntry(formData)
      .then((newEntry) => {
        setEntries([...entries, newEntry]);
        enqueueToast({
          level: "info",
          message: "Successfully created new todo entry.",
        });
      })
      .catch((error) => {
        enqueueToast({ level: "error", message: `${error}`, lifespan: "inf" });
      });
  }

  function removeEntry(id: string) {
    deleteEntry(id)
      .then(() => {
        setEntries((currentEntries) =>
          currentEntries.filter((entry) => entry.Id !== id)
        );
        enqueueToast({
          level: "info",
          message: "Successfully deleted todo entry.",
        });
      })
      .catch((error) => {
        enqueueToast({ level: "error", message: `${error}`, lifespan: "inf" });
      });
  }

  return (
    <div className={styles.table}>
      <AddTodoEntryForm formAction={addEntry} />
      <div className={styles.headingBar}>
        <div className={styles.firstHeading}>
          <h2 className={utilStyles.headingLg}>Description</h2>
        </div>
        <div className={styles.secondHeading}>
          <h2 className={utilStyles.headingLg}>Date Added</h2>
        </div>
        <div className={styles.fillerBlock}></div>
      </div>
      <div>
        {entries.map((item, i) => (
          <Fragment key={item.Id}>
            <TodoItem item={item} deleteItem={() => removeEntry(item.Id)} />
            {i < entries.length - 1 && <hr />}
          </Fragment>
        ))}
      </div>
    </div>
  );
}
