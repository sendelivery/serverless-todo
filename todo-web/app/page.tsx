import {
  ENTRIES_CACHE_TAG,
  todoApiEndpoint,
  todoApiKey,
} from "@/lib/serverConsts";
import { type TodoEntry } from "@/lib/todoClient";
import ToastQueueProvider from "@/components/ToastQueueProvider";
import TodoSection from "@/components/TodoSection";

export default async function Page() {
  const response = await fetch(todoApiEndpoint, {
    headers: {
      "x-api-key": todoApiKey,
    },
    next: { tags: [ENTRIES_CACHE_TAG] },
  });
  const entries: TodoEntry[] = await response.json();

  // TODO: Error Boundary here?

  return (
    <ToastQueueProvider>
      <TodoSection entries={entries} />
    </ToastQueueProvider>
  );
}
