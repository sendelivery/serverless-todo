"use client";

import { Fragment, useContext, useState } from "react";
import utilStyles from "@/styles/utilities.css";
import styles from "./styles.css";
import { type TodoEntry } from "@/lib/todoClient";
import TodoItem from "../TodoItem";
import AddTodoEntryForm from "../AddTodoEntryForm";
import { createEntry } from "@/app/actions";
import { ToastQueueContext } from "../ToastQueueProvider";

type TodoSectionProps = {
  entries: TodoEntry[];
};

export default function TodoSection(props: TodoSectionProps) {
  const [entries, setEntries] = useState<TodoEntry[]>(props.entries);
  const { enqueueToast } = useContext(ToastQueueContext);

  function addEntry(formData: FormData) {
    createEntry(formData)
      .then((newEntry) => {
        setEntries([...entries, newEntry]);
        enqueueToast({
          level: "info",
          message: "Successfully created new todo entry.",
        });
        // TODO: we should invalidate the GET cache tag here...
      })
      .catch((error) => {
        enqueueToast({
          level: "error",
          message: `${error}`,
        });
      });
  }

  const deleteEntry = (id: string) => {
    const filtered = entries.filter((item) => item.Id !== id);
    setEntries(filtered);
  };

  return (
    <div className={styles.table}>
      <AddTodoEntryForm formAction={addEntry} />
      <div className={styles.headingBar}>
        <div className={styles.firstHeading}>
          <h2 className={utilStyles.headingXl}>Description</h2>
        </div>
        <div className={styles.secondHeading}>
          <h2 className={utilStyles.headingXl}>Date Added</h2>
        </div>
        <div className={styles.fillerBlock}></div>
      </div>
      <div>
        {entries.map((item, i) => (
          <Fragment key={item.Id}>
            <TodoItem item={item} deleteItem={() => deleteEntry(item.Id)} />
            {i < entries.length - 1 && <hr />}
          </Fragment>
        ))}
      </div>
    </div>
  );
}
