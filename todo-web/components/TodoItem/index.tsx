import type { TodoItem as TodoItemType } from "@/lib/getTodoItems";
import styles from "./styles.css";
import CheckboxWithLabel from "../Checkbox";

export default function TodoItem(props: TodoItemType) {
  const { date, description, completed } = props;

  return (
    <div className={styles.todoItem}>
      <CheckboxWithLabel label={description} />
      <p>
        {date} - {completed ? "true" : "false"}
      </p>
    </div>
  );
}
