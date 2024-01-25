# serverless-todo-app

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./docs/assets/images/serverless_todo_logo_label_dark.svg">
    <img src="docs/assets/images/serverless_todo_logo_label.svg" width="70%">
  </picture>
</p>

Serverless Todo is a simple web app for keeping track of the things you have... _to do_. Built entirely just to get some practice with Next.js and Python, and to cement some of my AWS / systems design knowledge.

---

## Table of Contents

- [CICD Pipeline](#cicd-pipeline)
- [Ephemeral Environments](#ephemeral-environments)

---

## CICD Pipeline

The CICD pipeline has been built using CDK Pipelines and should be used to handle all deployments; due to the scope of the project, automated deployments are only made to the production environment.

To get started with deploying, simply run `cdk deploy TodoPipelineStack` in the project root. This command only needs to be run once, after which the pipeline will have been created in your AWS account. A CodePipeline execution will then automatically trigger, deploying the remaining CloudFormation stacks which correspond to the actual application resources.

Subsequent deployments can be performed simply by pushing commits (ideally as approved pull requests) to the main branch, each commit will trigger a new CodePipeline execution!

## Ephemeral Environments

During development, it may be helpful to spin up ephemeral environments; short-lived copies of the application stack that correspond to the feature being worked on.

A shell script has been written for this exact purpose! It acts as a wrapper to the `cdk deploy` command, meaning you can pass in the same command line options. Try `./scripts/deploy_ephemeral --hotswap`, or use a non-default AWS account using the `--profile` option!

Basic usage of the [deploy_ephemeral](./scripts/deploy_ephemeral) script looks like:

1. Checkout a new branch e.g. `git checkout feature/update-descriptions`
2. From the root directory, run `./scripts/deploy_ephemeral`

This will synthesize new stateful and stateless stacks, creating AWS resources with the branch name added on as a prefix, e.g. `feature-update-descriptions-TodoEntriesTable`.
