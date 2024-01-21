function tryToRetrieveEnvironmentVariables() {
  const endpoint = process.env.TODO_API_ENDPOINT;
  const key = process.env.TODO_API_KEY;

  if (!endpoint || !key) {
    throw new Error(
      `Unable to retrieve environment variables, TODO_API_ENDPOINT: ${endpoint}, TODO_API_KEY: ${key}`
    );
  }

  return [endpoint, key];
}

export const [todoApiEndpoint, todoApiKey] =
  tryToRetrieveEnvironmentVariables();

export const ENTRIES_CACHE_TAG = "entries_cache";
