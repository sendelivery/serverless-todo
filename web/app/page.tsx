import { ENTRIES_CACHE_TAG, todoApiEndpoint } from "@/lib/serverConsts";
import { type TodoEntry } from "@/lib/types";
import ToastQueueProvider from "@/components/ToastQueueProvider";
import TodoSection from "@/components/TodoSection";

export default async function Page() {
  let entries: TodoEntry[] = [];

  if (todoApiEndpoint) {
    const response = await fetch(todoApiEndpoint, {
      next: {
        tags: [ENTRIES_CACHE_TAG],
      },
    });

    console.log({ response });

    entries = await response.json();

    console.log({ entries });
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
