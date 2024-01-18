import styles from "./styles.css";
import { type TodoEntry } from "@/lib/todoClient";
import CheckboxWithLabel from "../Checkbox";
import { SimpleButton } from "../Button";

export type TodoItemProps = {
  item: TodoEntry;
  checkItem: () => void;
  deleteItem: () => void;
};

export default function TodoItem(props: TodoItemProps) {
  const { item } = props;

  const handleCheck = () => {
    props.checkItem();
  };

  return (
    <div className={styles.todoItem}>
      <div className={styles.checkboxContainer}>
        <CheckboxWithLabel
          label={item.Description}
          defaultChecked={item.Completed}
          setChecked={handleCheck}
        />
      </div>
      <div className={styles.dateContainer}>
        <p>
          {new Date(item.DateCreated).toLocaleDateString("en-GB", {
            day: "numeric",
            month: "short",
          })}
        </p>
      </div>
      <SimpleButton onClick={props.deleteItem} simpleStyle="cross" />
    </div>
  );
}
