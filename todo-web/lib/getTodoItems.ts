const data = [
  { date: "2023-11-26T10:10:22.296Z", description: "Hello", completed: true },
  { date: "2023-11-26T10:10:22.296Z", description: "World", completed: true },
  { date: "2023-11-26T10:10:22.296Z", description: "This", completed: false },
  { date: "2023-11-26T10:10:22.296Z", description: "Is", completed: false },
  { date: "2023-11-26T10:10:22.296Z", description: "My", completed: false },
  { date: "2023-11-26T10:10:22.296Z", description: "Todo", completed: false },
  { date: "2023-11-26T10:10:22.296Z", description: "App!", completed: false },
];
export type TodoItem = (typeof data)[0];

export async function getTodoItems(): Promise<TodoItem[]> {
  return new Promise((resolve) => {
    resolve(data);
  });
}
