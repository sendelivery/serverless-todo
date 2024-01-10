let data = [
  {
    Id: 0,
    DateCreated: 1704837140643,
    Description: "Finalise Todo app UI and system designs",
    Completed: true,
  },
  {
    Id: 1,
    DateCreated: 1704837240643,
    Description: "Implement Todo app frontend",
    Completed: true,
  },
  {
    Id: 2,
    DateCreated: 1704837340643,
    Description: "Draft Todo app AWS infrastructure as IaC",
    Completed: false,
  },
  {
    Id: 3,
    DateCreated: 1704837440643,
    Description: "Implement CRUD Lambdas for Todo app",
    Completed: false,
  },
  {
    Id: 4,
    DateCreated: 1704837540643,
    Description:
      "Hook up Todo app frontend to backend via API Gateway and Next.js API routes",
    Completed: false,
  },
  {
    Id: 5,
    DateCreated: 1704837640643,
    Description: "Run a full test of Todo app",
    Completed: false,
  },
  {
    Id: 6,
    DateCreated: 1704837740643,
    Description: "Fix bugs and clean up code",
    Completed: false,
  },
  {
    Id: 7,
    DateCreated: 1704837840643,
    Description: "Create documentation for Todo app",
    Completed: false,
  },
  {
    Id: 8,
    DateCreated: 1704837940643,
    Description: "Bask in glory! Dynamo BATCH!!",
    Completed: false,
  },
];

export type TodoEntry = {
  Id: number;
  DateCreated: number;
  Description: string;
  Completed: boolean;
};

export type TodoEntryInput = {
  DateCreated: number;
  Description: string;
  Completed: boolean;
};

export async function getTodoEntries(): Promise<TodoEntry[]> {
  return new Promise((resolve) => {
    resolve(data);
  });
}

export async function upsertTodoEntry(item: TodoEntryInput): Promise<number> {
  return new Promise((resolve) => {
    const Id = data.length * (Date.now() % 100000);
    data.push({ ...item, Id });
    resolve(200);
  });
}

export async function deleteTodoEntry(Id: number): Promise<number> {
  return new Promise((resolve, reject) => {
    let found = false;

    for (let i = 0; i < data.length && !found; ++i) {
      if (data[i].Id === Id) {
        found = true;
        data.splice(Id, 1);
      }
    }

    found ? resolve(200) : reject(400);
  });
}
