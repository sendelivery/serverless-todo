let data = [
  {
    Id: "0",
    DateCreated: 1704837140643,
    Description: "Finalise Todo app UI and system designs",
    Completed: true,
  },
  {
    Id: "1",
    DateCreated: 1704837240643,
    Description: "Implement Todo app frontend",
    Completed: true,
  },
];

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

export async function getTodoEntries(): Promise<TodoEntry[]> {
  return new Promise((resolve) => {
    resolve(data);
  });
}

export async function upsertTodoEntry(item: TodoEntryInput): Promise<number> {
  return new Promise((resolve) => {
    const Id = (data.length * (Date.now() % 100000)).toString();
    data.push({ ...item, Id });
    resolve(200);
  });
}

export async function deleteTodoEntry(Id: string): Promise<number> {
  return new Promise((resolve, reject) => {
    let found = false;

    for (let i = 0; i < data.length && !found; ++i) {
      if (data[i].Id === Id) {
        found = true;
        data.splice(i, 1);
        break;
      }
    }

    found ? resolve(200) : reject(400);
  });
}
