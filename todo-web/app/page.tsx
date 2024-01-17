import { todoApiEndpoint, todoApiKey } from "@/lib/serverConsts";
import { type TodoEntry } from "@/lib/todoClient";
import ToastQueueProvider from "@/components/ToastQueueProvider";
import TodoSection from "@/components/TodoSection";

export default async function Page() {
  // No need to worry about caching or revalidation because our app has no routing.
  const response = await fetch(todoApiEndpoint, {
    headers: {
      "x-api-key": todoApiKey,
    },
  });
  const entries: TodoEntry[] = await response.json();

  // TODO: Error Boundary here?

  return (
    <ToastQueueProvider>
      <TodoSection entries={entries} />
    </ToastQueueProvider>
  );
}
