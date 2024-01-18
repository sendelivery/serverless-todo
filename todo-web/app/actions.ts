"use server";

import {
  ENTRIES_CACHE_TAG,
  todoApiEndpoint,
  todoApiKey,
} from "@/lib/serverConsts";
import { type TodoEntry, type TodoEntryInput } from "@/lib/todoClient";
import { revalidateTag } from "next/cache";

export async function serverPostEntry(formData: FormData) {
  let input = formData.get("description") as string;
  input = input.trim();

  if (!input) {
    throw new Error("Invalid input error");
  }

  const todoEntryInput: TodoEntryInput = {
    DateCreated: new Date().getTime(),
    Description: input,
    Completed: false,
  };

  const response = await fetch(todoApiEndpoint, {
    method: "POST",
    headers: { "x-api-key": todoApiKey, "Content-Type": "application/json" },
    cache: "no-store", // Not strictly needed as form submission results in hard refresh
    body: JSON.stringify(todoEntryInput),
  });

  if (!response.ok) {
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
  const response = await fetch(todoApiEndpoint, {
    method: "PUT",
    headers: { "x-api-key": todoApiKey, "Content-Type": "application/json" },
    cache: "no-store",
    body: JSON.stringify({ Id: id, Completed: completed }),
  });

  if (!response.ok) {
    throw new Error("Unbale to update todo entry. Please try again later.");
  }

  revalidateTag(ENTRIES_CACHE_TAG);
}

export async function serverDeleteEntry(id: string) {
  // Deletes are fine to be cached, unless something's gone wrong in the UI the
  // user shouldn't be able to resubmit the same delete request.
  const response = await fetch(todoApiEndpoint, {
    method: "DELETE",
    headers: { "x-api-key": todoApiKey, "Content-Type": "application/json" },
    body: JSON.stringify({ Id: id }),
  });

  if (!response.ok) {
    throw new Error("Unable to delete todo entry. Please try again later.");
  }

  revalidateTag(ENTRIES_CACHE_TAG);
}
