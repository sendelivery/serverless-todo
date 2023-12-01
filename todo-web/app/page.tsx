import Table from "@/components/Table";
import { getTodoEntries, TodoEntry } from "@/lib/todoClient";

export default async function Page() {
  // TODO: use context here?
  const items: TodoEntry[] = await getTodoEntries();

  return (
    <>
      <Table items={items} />
    </>
  );
}
