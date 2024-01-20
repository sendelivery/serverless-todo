export type TodoEntry = {
  Id: string;
  DateCreated: number;
  Description: string;
  Completed: boolean;
};

export type TodoEntryInput = Pick<
  TodoEntry,
  "Completed" | "DateCreated" | "Description"
>;
