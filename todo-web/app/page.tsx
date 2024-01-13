import Table from "@/components/Table";
import { todoApiEndpoint, todoApiKey } from "@/lib/consts";
import type { TodoEntry } from "@/lib/todoClient";

export default async function Page() {
  const response = await fetch(`${todoApiEndpoint}`, {
    headers: {
      "x-api-key": todoApiKey,
    },
    next: { revalidate: 7200 },
  });

  const data = await response.json();
  const items: TodoEntry[] = data;

  return <Table items={items} />;
}
