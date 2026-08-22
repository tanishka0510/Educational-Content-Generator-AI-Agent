The Orchestrator Agent is the central coordinator of the Educational AI Multi-Agent Platform.

It receives every request from the API Gateway, understands the user's intent, selects the appropriate AI agent(s), manages workflow execution, aggregates outputs, handles failures, and returns a unified response to the frontend.

The orchestrator itself does not generate educational content. It only coordinates specialized agents.


| Responsibility    | Description                             |
| ----------------- | --------------------------------------- |
| Receive Request   | Accept every request from FastAPI       |
| Detect Intent     | Identify the user's request type        |
| Route Request     | Select the required agent(s)            |
| Manage Workflow   | Execute agents in the correct order     |
| Share State       | Pass data between agents                |
| Aggregate Results | Merge outputs from multiple agents      |
| Error Handling    | Handle failures and retries             |
| Return Response   | Send one final response to the frontend |


| Agent              | Responsibility                          |
| ------------------ | --------------------------------------- |
| Content Processing | Extract and prepare educational content |
| Educational        | Generate educational materials          |
| Multimedia         | Audio, speech, multimedia generation    |


                 USER
                   │
                   ▼
            FastAPI API Gateway
                   │
                   ▼
         ┌────────────────────┐
         │  ORCHESTRATOR       │
         └────────────────────┘
                   │
        ┌──────────┼───────────┐
        │          │           │
        ▼          ▼           ▼
   Content     Educational   Multimedia
   Processing      Agent        Agent
        │          │           │
        └──────────┼───────────┘
                   ▼
          Response Aggregator
                   ▼
                 Frontend


list of all the intends

UPLOAD

QA

SUMMARY

QUIZ

FLASHCARDS

LEARNING_OBJECTIVES

RESOURCE_SEARCH

COMPARE

EXPLANATION

PROGRAMMING

MATHEMATICS

ASSIGNMENT

STUDY_PLAN

MULTIMEDIA

MIXED

FOLLOW_UP

GENERAL_KNOWLEDGE

ADMIN

WORKFLOW 

| Intent     | Workflow                                          |
| ---------- | ------------------------------------------------- |
| Upload     | Orchestrator → Content Processing                 |
| Summary    | Orchestrator → Educational                        |
| Quiz       | Orchestrator → Educational                        |
| QA         | Orchestrator → Content Processing → Educational   |
| Multimedia | Orchestrator → Multimedia                         |
| Mixed      | Orchestrator → Content → Educational → Multimedia |
