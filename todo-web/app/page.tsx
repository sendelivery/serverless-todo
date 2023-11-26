import TodoItem from "@/components/TodoItem";
import { getTodoItems, TodoItem as TodoItemType } from "@/lib/getTodoItems";

export default async function Page() {
  const items: TodoItemType[] = await getTodoItems();

  return items.map((item, i) => (
    <TodoItem
      date={item.date}
      description={item.description}
      completed={item.completed}
      key={`${item}-${i}`}
    />
  ));
}
