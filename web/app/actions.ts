"use server";

import { ENTRIES_CACHE_TAG, todoApiEndpoint } from "@/lib/serverConsts";
import { type TodoEntry, type TodoEntryInput } from "@/lib/types";
import { revalidateTag } from "next/cache";

function validateEndpointIsDefined() {
  if (!todoApiEndpoint) {
    throw new Error(
      "Todo API endpoint is not defined, please check environment variables."
    );
  }

  return todoApiEndpoint;
}

export async function serverPostEntry(formData: FormData) {
  let input = formData.get("description") as string;
  input = input.trim();

  const endpoint = validateEndpointIsDefined();

  if (!input) {
    console.error({
      message: "Invalid input when creating new todo entry.",
      input: JSON.stringify(input),
    });
    throw new Error("Invalid input error");
  }

  const todoEntryInput: TodoEntryInput = {
    DateCreated: new Date().getTime(),
    Description: input,
    Completed: false,
  };

  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-store", // Not strictly needed as form submission results in hard refresh
    body: JSON.stringify(todoEntryInput),
  });

  if (!response.ok) {
    console.error({
      message: "Received a non 2XX response when creating new todo entry.",
      input: JSON.stringify(todoEntryInput),
      response: JSON.stringify(response),
    });
    throw new Error("Unable to create new todo entry. Please try again later.");
  }

  revalidateTag(ENTRIES_CACHE_TAG);

  const id = await response.text();
  const todoEntry: TodoEntry = {
    ...todoEntryInput,
    Id: id,
  };

  return todoEntry;
}

export async function serverPutEntry(id: string, completed: boolean) {
  const endpoint = validateEndpointIsDefined();

  const proposedUpdate = JSON.stringify({ Id: id, Completed: completed });

  const response = await fetch(endpoint, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    body: proposedUpdate,
  });

  if (!response.ok) {
    console.error({
      message: "Received a non 2XX response when updating a todo entry.",
      proposedUpdate: JSON.stringify(proposedUpdate),
      response: JSON.stringify(response),
    });
    throw new Error("Unbale to update todo entry. Please try again later.");
  }

  revalidateTag(ENTRIES_CACHE_TAG);
}

export async function serverDeleteEntry(id: string) {
  const endpoint = validateEndpointIsDefined();

  // Deletes are fine to be cached, unless something's gone wrong in the UI the
  // user shouldn't be able to resubmit the same delete request.
  const response = await fetch(endpoint, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ Id: id }),
  });

  if (!response.ok) {
    console.error({
      message: "Received a non 2XX response when deleting a todo entry.",
      id,
      response: JSON.stringify(response),
    });
    throw new Error("Unable to delete todo entry. Please try again later.");
  }

  revalidateTag(ENTRIES_CACHE_TAG);
}
