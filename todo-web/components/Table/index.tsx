"use client";

import { Fragment, useState } from "react";
import utilStyles from "@/styles/utilities.css";
import styles from "./styles.css";
import type { TodoEntry, TodoEntryInput } from "@/lib/todoClient";
import TodoItem from "../TodoItem";
import AddTodoItemForm from "../AddTodoItemForm";

type TableProps = {
  items: TodoEntry[];
};

export default function Table(props: TableProps) {
  const [items, setItems] = useState<TodoEntry[]>(props.items);

  const addItem = (item: TodoEntryInput) => {
    const itemWithId = { ...item, Id: items.length };
    setItems([...items, itemWithId]);
  };

  const deleteItem = (id: number) => {
    const filtered = items.filter((item) => item.Id !== id);
    setItems(filtered);
  };

  return (
    <div className={styles.table}>
      <AddTodoItemForm action={addItem} />
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
        {items.map((item, i) => (
          <Fragment key={item.Id}>
            <TodoItem item={item} deleteItem={() => deleteItem(item.Id)} />
            {i < items.length - 1 && <hr />}
          </Fragment>
        ))}
      </div>
    </div>
  );
}
