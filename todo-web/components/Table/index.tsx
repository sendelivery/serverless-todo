"use client";

import { useState } from "react";
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
    const itemWithId = { ...item, id: items.length };
    setItems([...items, itemWithId]);
  };

  const deleteItem = (id: number) => {
    const filtered = items.filter((item) => item.id !== id);
    setItems(filtered);
  };

  return (
    <div className={styles.table}>
      <AddTodoItemForm action={addItem} />
      <div className={styles.headings}>
        <h2>Description</h2>
        <h2>Date Added</h2>
      </div>
      <div>
        {items.map((item, i) => (
          <>
            <TodoItem
              key={item.id}
              item={item}
              deleteItem={() => deleteItem(item.id)}
            />
            {i < items.length - 1 && <hr />}
          </>
        ))}
      </div>
    </div>
  );
}
