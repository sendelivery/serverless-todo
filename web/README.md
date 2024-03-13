# Serverless Todo Web App

The web application of Serverless Todo is powered by [Next.js](https://nextjs.org/) and bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

The project is written in [TypeScript](https://www.typescriptlang.org/) and uses [Vanilla Extract](https://github.com/vanilla-extract-css/vanilla-extract) for styling.

## Getting Started

To get started working locally, first navigate into the `web/` directory from the project root:

```bash
cd web
```

Next, install all project dependencies:

```bash
npm install
# or
yarn install
# or
pnpm install
# or
bun install
```

Finally, run the development server like so (make sure your environment variables are set up correctly, see below):

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the running app. Edit any page or component, save your changes, and the app will auto-update displaying your latest changes. This is thanks to Next.js' built-in [Fast Refresh](https://nextjs.org/docs/architecture/fast-refresh) feature.

## Environment Set Up

The necessary environment variable configuration required to productively work on the web application locally is described in the table below. [Here's an example](.env.example).

| Variable Name       | Required | Description                                                                                                                                                                                                                                        |
| ------------------- | :------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `TODO_API_ENDPOINT` |    ✅    | The API endpoint by which our web app can communicate with backend services. See the [ephemeral environments](../README.md#ephemeral-environments) section on the root page for information on how to obtain one for integrated local development. |

## Local Build and Deploy

The Serverless Todo web application is configured to be built as a Docker image and run on a container in production.

At times, it may be useful to mimic this locally. To accomplish this, first ensure you have [Docker](https://docs.docker.com/get-docker/) installed on your machine. Then run the following:

```bash
# assuming your terminal is in the web/ directory
# build the docker image
docker build -t web-app .
# run your container, passing in the correct endpoint
docker run \
  -p 3000:3000 \
  -e TODO_API_ENDPOINT="<api_endpoint>" \
  web-app
```

## Learn More

To learn more about Next.js and Docker builds, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.
- [Building Your Application as a Docker Image](https://nextjs.org/docs/app/building-your-application/deploying#docker-image) - Next.js official documentation.
- [Docker Manuals](https://docs.docker.com/manuals/) - Docker official documentation and user manuals.
