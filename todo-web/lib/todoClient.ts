let data = [
  {
    id: 0,
    date: "2023-11-26T10:10:22.296Z",
    description: "Hello",
    completed: true,
  },
  {
    id: 1,
    date: "2023-11-26T10:10:22.296Z",
    description: "World",
    completed: true,
  },
  {
    id: 2,
    date: "2023-11-26T10:10:22.296Z",
    description: "This",
    completed: false,
  },
  {
    id: 3,
    date: "2023-11-26T10:10:22.296Z",
    description: "Is",
    completed: false,
  },
  {
    id: 4,
    date: "2023-11-26T10:10:22.296Z",
    description: "My",
    completed: false,
  },
  {
    id: 5,
    date: "2023-11-26T10:10:22.296Z",
    description: "Todo",
    completed: false,
  },
  {
    id: 6,
    date: "2023-11-26T10:10:22.296Z",
    description: "App!",
    completed: false,
  },
];

export type TodoItem = {
  date: string;
  description: string;
  completed: boolean;
};

export async function getTodoItems(): Promise<TodoItem[]> {
  return new Promise((resolve) => {
    resolve(data);
  });
}

export async function upsertTodoItem(item: TodoItem): Promise<number> {
  return new Promise((resolve) => {
    const id = data.length * (Date.now() % 100000);
    data.push({ id, ...item });
    resolve(200);
  });
}

export async function deleteTodoItem(id: number): Promise<number> {
  return new Promise((resolve, reject) => {
    let found = false;

    for (let i = 0; i < data.length && !found; ++i) {
      if (data[i].id === id) {
        found = true;
        data.splice(id, 1);
      }
    }

    found ? resolve(200) : reject(500);
  });
}
