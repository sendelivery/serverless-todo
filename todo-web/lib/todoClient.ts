let data = [
  {
    id: 0,
    date: "2023-11-26T10:10:22.296Z",
    description: "Finalise Todo app UI and system designs",
    completed: true,
  },
  {
    id: 1,
    date: "2023-11-26T10:10:22.296Z",
    description: "Implement Todo app frontend",
    completed: false,
  },
  {
    id: 2,
    date: "2023-11-26T10:10:22.296Z",
    description: "Draft Todo app AWS infrastructure as IaC",
    completed: false,
  },
  {
    id: 3,
    date: "2023-11-26T10:10:22.296Z",
    description: "Implement CRUD Lambdas for Todo app",
    completed: false,
  },
  {
    id: 4,
    date: "2023-11-26T10:10:22.296Z",
    description:
      "Hook up Todo app frontend to backend via API Gateway and Next.js API routes",
    completed: false,
  },
  {
    id: 5,
    date: "2023-11-26T10:10:22.296Z",
    description: "Run a full test of Todo app",
    completed: false,
  },
  {
    id: 6,
    date: "2023-11-26T10:10:22.296Z",
    description: "Fix bugs and clean up code",
    completed: false,
  },
  {
    id: 7,
    date: "2023-11-26T10:10:22.296Z",
    description: "Create documentation for Todo app",
    completed: false,
  },
  {
    id: 8,
    date: "2023-11-26T10:10:22.296Z",
    description: "Bask in glory!",
    completed: false,
  },
];

export type TodoEntry = {
  id: number;
  date: string;
  description: string;
  completed: boolean;
};

export type TodoEntryInput = {
  date: string;
  description: string;
  completed: boolean;
};

export async function getTodoEntries(): Promise<TodoEntry[]> {
  return new Promise((resolve) => {
    resolve(data);
  });
}

export async function upsertTodoEntry(item: TodoEntryInput): Promise<number> {
  return new Promise((resolve) => {
    const id = data.length * (Date.now() % 100000);
    data.push({ ...item, id });
    resolve(200);
  });
}

export async function deleteTodoEntry(id: number): Promise<number> {
  return new Promise((resolve, reject) => {
    let found = false;

    for (let i = 0; i < data.length && !found; ++i) {
      if (data[i].id === id) {
        found = true;
        data.splice(id, 1);
      }
    }

    found ? resolve(200) : reject(400);
  });
}
