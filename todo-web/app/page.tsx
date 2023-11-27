import Table from "@/components/Table";
import { getTodoItems, TodoItem as TodoItemType } from "@/lib/todoClient";

export default async function Page() {
  // TODO: use context here?
  const items: TodoItemType[] = await getTodoItems();

  return (
    <>
      <Table items={items} />
    </>
  );
}
