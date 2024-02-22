"use client";

import { Fragment, useContext, useState } from "react";
import utilStyles from "@/styles/utilities.css";
import styles from "./styles.css";
import { type TodoEntry } from "@/lib/types";
import TodoItem from "../TodoItem";
import AddTodoEntryForm from "../AddTodoEntryForm";
import {
  serverDeleteEntry,
  serverPostEntry,
  serverPutEntry,
} from "@/app/actions";
import { ToastQueueContext } from "../ToastQueueProvider";

function EmptySection() {
  return (
    <div className={utilStyles.centredText}>
      <h2 className={utilStyles.headingXl}>
        🎉 Congrats, your Todo list is{" "}
        <span className={utilStyles.highlightedText}>empty!</span>
      </h2>
      <p>
        <span className={utilStyles.italicText}>Forget something?</span> Add a
        new entry to your list above.
      </p>
    </div>
  );
}

type TodoSectionProps = {
  entries: TodoEntry[];
};

export default function TodoSection(props: TodoSectionProps) {
  const [entries, setEntries] = useState<TodoEntry[]>(props.entries);

  const { enqueueToast } = useContext(ToastQueueContext);

  // Below are our 3 server actions for creating, updating, and deleting entries respectively.
  function addEntry(formData: FormData) {
    serverPostEntry(formData)
      .then((newEntry) => {
        setEntries([...entries, newEntry]);
        enqueueToast({
          level: "info",
          message: "Successfully created new todo entry.",
        });
      })
      .catch(() => {
        enqueueToast({
          level: "error",
          message:
            "Sorry, we had trouble creating your Todo entry, please try again later.",
          lifespan: "inf",
        });
      });
  }

  function updateEntry(id: string, completed: boolean) {
    serverPutEntry(id, completed)
      .then(() => {
        const updatedEntries = entries.map((entry) => {
          if (entry.Id === id) {
            entry.Completed = completed;
          }
          return entry;
        });
        setEntries(updatedEntries);
        enqueueToast({
          level: "info",
          message: "Successfully updated todo entry.",
        });
      })
      .catch(() => {
        enqueueToast({
          level: "error",
          message:
            "Sorry, we had trouble updating your Todo entry, please try again later.",
          lifespan: "inf",
        });
      });
  }

  function removeEntry(id: string) {
    serverDeleteEntry(id)
      .then(() => {
        setEntries((currentEntries) =>
          currentEntries.filter((entry) => entry.Id !== id)
        );
        enqueueToast({
          level: "info",
          message: "Successfully deleted todo entry.",
        });
      })
      .catch(() => {
        enqueueToast({
          level: "error",
          message:
            "Sorry, we had trouble deleting your Todo entry, please try again later.",
          lifespan: "inf",
        });
      });
  }

  let body = <EmptySection />;

  if (entries.length) {
    body = (
      <>
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
          {entries.map((entry, i) => (
            <Fragment key={entry.Id}>
              <TodoItem
                item={entry}
                checkItem={() => updateEntry(entry.Id, !entry.Completed)}
                deleteItem={() => removeEntry(entry.Id)}
              />
              {i < entries.length - 1 && <hr />}
            </Fragment>
          ))}
        </div>
      </>
    );
  }

  return (
    <div className={styles.table}>
      <AddTodoEntryForm formAction={addEntry} />
      {body}
    </div>
  );
}
