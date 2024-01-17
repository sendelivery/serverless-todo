"use server";

import { todoApiEndpoint, todoApiKey } from "@/lib/serverConsts";
import { type TodoEntry, type TodoEntryInput } from "@/lib/todoClient";

export async function postEntry(formData: FormData) {
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
    body: JSON.stringify(todoEntryInput),
  });

  if (!response.ok) {
    throw new Error("Unable to create new todo entry. Please try again later.");
  }

  const id = await response.text();

  const todoEntry: TodoEntry = {
    ...todoEntryInput,
    Id: id,
  };

  return todoEntry;
}

export async function deleteEntry(id: string) {
  const response = await fetch(todoApiEndpoint, {
    method: "DELETE",
    headers: { "x-api-key": todoApiKey, "Content-Type": "application/json" },
    body: JSON.stringify({ Id: id }),
  });

  if (!response.ok) {
    throw new Error("Unable to delete todo entry. Please try again later.");
  }
}
