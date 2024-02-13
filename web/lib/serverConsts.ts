function tryToGetApiDetailsFromEnv() {
  // Unless we have an explicit string value, we'll default to undefined
  // as it's easier to work with.
  let endpoint = process.env.TODO_API_ENDPOINT || undefined;
  let key = process.env.TODO_API_KEY || undefined;

  console.info(
    `Retrieved API details from environment variables, TODO_API_ENDPOINT: ${endpoint}, TODO_API_KEY: ${key}`
  );

  return [endpoint, key];
}

export const [todoApiEndpoint, todoApiKey] = tryToGetApiDetailsFromEnv();

export const ENTRIES_CACHE_TAG = "entries_cache";
