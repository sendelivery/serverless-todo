import {
  ENTRIES_CACHE_TAG,
  todoApiEndpoint,
  todoApiKey,
} from "@/lib/serverConsts";
import { type TodoEntry } from "@/lib/types";
import ToastQueueProvider from "@/components/ToastQueueProvider";
import TodoSection from "@/components/TodoSection";

export default async function Page() {
  let entries: TodoEntry[] = [];

  if (todoApiEndpoint && todoApiKey) {
    const response = await fetch(todoApiEndpoint, {
      headers: { "x-api-key": todoApiKey },
      next: { tags: [ENTRIES_CACHE_TAG] },
    });

    entries = await response.json();
  } else {
    console.warn(
      "API endpoint and or key are undefined, please ensure environment variables are correctly set."
    );
  }

  return (
    <ToastQueueProvider>
      <TodoSection entries={entries} />
    </ToastQueueProvider>
  );
}
