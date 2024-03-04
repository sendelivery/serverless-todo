import { ENTRIES_CACHE_TAG, todoApiEndpoint } from "@/lib/serverConsts";
import { type TodoEntry } from "@/lib/types";
import ToastQueueProvider from "@/components/ToastQueueProvider";
import TodoSection from "@/components/TodoSection";

export const dynamic = "force-dynamic";

export default async function Page() {
  let entries: TodoEntry[] = [];

  if (todoApiEndpoint) {
    try {
      const response = await fetch(todoApiEndpoint, {
        next: {
          tags: [ENTRIES_CACHE_TAG],
        },
      });
      console.debug({ response });

      entries = await response.json();
      console.log({ message: "Successfully fetched entries!", entries });
    } catch (error) {
      console.error({
        message: `Failed to fetch entries with the following error: ${error}`,
      });
    }
  } else {
    console.warn(
      "API endpoint is undefined, please ensure environment variables are correctly set."
    );
  }

  return (
    <ToastQueueProvider>
      <TodoSection entries={entries} />
    </ToastQueueProvider>
  );
}
