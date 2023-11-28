"use client";

import { useState } from "react";
import styles from "./styles.css";
import type { TodoItem as TodoItemType } from "@/lib/todoClient";
import TodoItem from "../TodoItem";
import AddTodoItemForm from "../AddTodoItemForm";

type TableProps = {
  items: TodoItemType[];
};

export default function Table(props: TableProps) {
  const [items, setItems] = useState<TodoItemType[]>(props.items);

  const setItem = (item: TodoItemType) => {
    setItems([...items, item]);
  };

  return (
    <div className={styles.table}>
      <div className={styles.headings}>
        <h2>Description</h2>
        <h2>Date Added</h2>
      </div>
      <div>
        {items.map((item, i) => (
          <TodoItem
            date={item.date}
            description={item.description}
            completed={item.completed}
            key={`${item}-${i}`}
          />
        ))}
      </div>
      <AddTodoItemForm action={setItem} />
    </div>
  );
}
