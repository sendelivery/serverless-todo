function tryToGetApiDetailsFromEnv() {
  // Unless we have an explicit string value, we'll default to undefined
  // as it's easier to work with.
  let endpoint = process.env.TODO_API_ENDPOINT || undefined;

  // Our web app only interacts with the /entries resource, so we'll just hardcode
  // that into our endpoint here.
  endpoint = endpoint && `${endpoint}entries`;

  console.info(
    `Retrieved API details from environment variables, TODO_API_ENDPOINT: ${endpoint}`
  );

  return endpoint;
}

export const todoApiEndpoint = tryToGetApiDetailsFromEnv();

export const ENTRIES_CACHE_TAG = "entries_cache";
