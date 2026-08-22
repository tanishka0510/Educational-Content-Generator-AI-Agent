1. Introduction

The Routing Matrix is the central decision document for the Orchestrator Agent. It defines how user requests are interpreted and routed through the system. Every routing component—including the Intent Detector, Workflow Manager, Execution Planner, Agent Selector, and Router—uses this matrix as the single source of truth.

Instead of embedding routing logic across multiple files, all routing decisions are defined here. This ensures consistency, simplifies maintenance, and makes it easy to introduce new workflows or query types in the future.

2. Purpose

The Routing Matrix serves the following objectives:

Standardize routing decisions across the Orchestrator.
Map each supported query type to its corresponding intent.
Determine the appropriate workflow category.
Define the execution strategy for each workflow.
Identify which agent(s) should execute the request.
Reduce duplicated routing logic across modules.
Simplify future expansion of the system.

3. Supported Query Types

The Orchestrator currently supports the following query types.

| No. | Query Type          | Description                               |
| --- | ------------------- | ----------------------------------------- |
| 1   | Upload              | Upload and process documents              |
| 2   | QA                  | Question answering using uploaded content |
| 3   | Summary             | Generate summaries                        |
| 4   | Quiz                | Generate quizzes                          |
| 5   | Flashcards          | Generate flashcards                       |
| 6   | Learning Objectives | Generate learning objectives              |
| 7   | Multimedia          | Generate multimedia content               |
| 8   | Resource Search     | Recommend learning resources              |
| 9   | Compare             | Compare topics or concepts                |
| 10  | Explanation         | Explain a concept                         |
| 11  | Programming         | Programming-related educational tasks     |
| 12  | Mathematics         | Mathematical explanations and solutions   |
| 13  | Assignment          | Generate assignments                      |
| 14  | Study Plan          | Generate study plans                      |
| 15  | Mixed Query         | Multiple requests in a single query       |
| 16  | Follow-up           | Continue previous conversation            |
| 17  | General Knowledge   | General educational questions             |
| 18  | Admin               | Administrative operations                 |


4. Intent Mapping

| Query Type          | Detected Intent     |
| ------------------- | ------------------- |
| Upload              | UPLOAD              |
| QA                  | QA                  |
| Summary             | SUMMARY             |
| Quiz                | QUIZ                |
| Flashcards          | FLASHCARDS          |
| Learning Objectives | LEARNING_OBJECTIVES |
| Keywords            | KEYWORDS            |
| Concepts            | CONCEPTS            |
| Multimedia          | MULTIMEDIA          |
| Resource Search     | RESOURCE_SEARCH     |
| Compare             | COMPARE             |
| Explanation         | EXPLANATION         |
| Programming         | PROGRAMMING         |
| Mathematics         | MATHEMATICS         |
| Assignment          | ASSIGNMENT          |
| Study Plan          | STUDY_PLAN          |
| Mixed Query         | MIXED_QUERY         |
| Follow-up           | FOLLOW_UP           |
| General Knowledge   | GENERAL_KNOWLEDGE   |
| Admin               | ADMIN               |


5. Workflow Mapping

| Intent              | Workflow Category  |
| ------------------- | ------------------ |
| UPLOAD              | CONTENT_PROCESSING |
| QA                  | EDUCATIONAL        |
| SUMMARY             | EDUCATIONAL        |
| QUIZ                | EDUCATIONAL        |
| FLASHCARDS          | EDUCATIONAL        |
| LEARNING_OBJECTIVES | EDUCATIONAL        |
| KEYWORDS            | EDUCATIONAL        |
| CONCEPTS            | EDUCATIONAL        |
| MULTIMEDIA          | MULTIMEDIA         |
| RESOURCE_SEARCH     | EDUCATIONAL        |
| COMPARE             | EDUCATIONAL        |
| EXPLANATION         | EDUCATIONAL        |
| PROGRAMMING         | EDUCATIONAL        |
| MATHEMATICS         | EDUCATIONAL        |
| ASSIGNMENT          | EDUCATIONAL        |
| STUDY_PLAN          | EDUCATIONAL        |
| MIXED_QUERY         | COMPOSITE          |
| FOLLOW_UP           | CONTEXT            |
| GENERAL_KNOWLEDGE   | EDUCATIONAL        |
| ADMIN               | SYSTEM             |


6. Execution Strategy Mapping

| Workflow           | Execution Strategy | Description                         |
| ------------------ | ------------------ | ----------------------------------- |
| CONTENT_PROCESSING | SINGLE             | Execute one agent                   |
| EDUCATIONAL        | SINGLE             | Execute one agent                   |
| MULTIMEDIA         | SINGLE             | Execute one agent                   |
| COMPOSITE          | SEQUENTIAL         | Execute multiple agents in sequence |
| CONTEXT            | CONTEXT_BASED      | Use conversation history            |
| SYSTEM             | SINGLE             | Execute system operation            |


7. Agent Selection Mapping

| Workflow           | Selected Agents                               |
| ------------------ | --------------------------------------------- |
| CONTENT_PROCESSING | Content Processing Agent                      |
| EDUCATIONAL        | Educational Content Generator Agent           |
| MULTIMEDIA         | Multimedia Agent                              |
| COMPOSITE          | Content Processing → Educational → Multimedia |
| CONTEXT            | Orchestrator Agent                            |
| SYSTEM             | Content Processing Agent                      |


8. Complete Routing Decision Table

| Query Type          | Intent              | Workflow           | Strategy      | Selected Agents                               |
| ------------------- | ------------------- | ------------------ | ------------- | --------------------------------------------- |
| Upload              | UPLOAD              | CONTENT_PROCESSING | SINGLE        | Content Processing                            |
| QA                  | QA                  | EDUCATIONAL        | SEQUENTIAL    | Content Processing → Educational              |
| Summary             | SUMMARY             | EDUCATIONAL        | SINGLE        | Educational                                   |
| Quiz                | QUIZ                | EDUCATIONAL        | SINGLE        | Educational                                   |
| Flashcards          | FLASHCARDS          | EDUCATIONAL        | SINGLE        | Educational                                   |
| Learning Objectives | LEARNING_OBJECTIVES | EDUCATIONAL        | SINGLE        | Educational                                   |
| Keywords            | KEYWORDS            | EDUCATIONAL        | SINGLE        | Educational                                   |
| Concepts            | CONCEPTS            | EDUCATIONAL        | SINGLE        | Educational                                   |
| Multimedia          | MULTIMEDIA          | MULTIMEDIA         | SINGLE        | Multimedia                                    |
| Resource Search     | RESOURCE_SEARCH     | EDUCATIONAL        | SINGLE        | Educational                                   |
| Compare             | COMPARE             | EDUCATIONAL        | SINGLE        | Educational                                   |
| Explanation         | EXPLANATION         | EDUCATIONAL        | SINGLE        | Educational                                   |
| Programming         | PROGRAMMING         | EDUCATIONAL        | SINGLE        | Educational                                   |
| Mathematics         | MATHEMATICS         | EDUCATIONAL        | SINGLE        | Educational                                   |
| Assignment          | ASSIGNMENT          | EDUCATIONAL        | SINGLE        | Educational                                   |
| Study Plan          | STUDY_PLAN          | EDUCATIONAL        | SINGLE        | Educational                                   |
| Mixed Query         | MIXED_QUERY         | COMPOSITE          | SEQUENTIAL    | Content Processing → Educational → Multimedia |
| Follow-up           | FOLLOW_UP           | CONTEXT            | CONTEXT_BASED | Orchestrator                                  |
| General Knowledge   | GENERAL_KNOWLEDGE   | EDUCATIONAL        | SINGLE        | Educational                                   |
| Admin               | ADMIN               | SYSTEM             | SINGLE        | Content Processing                            |


9. Mixed Query Routing

Example 1

User Query

Upload this PDF, generate a summary, and create a quiz.

Routing Flow

User Request
      │
      ▼
Intent Detector
      │
      ▼
MIXED_QUERY
      │
      ▼
Workflow Manager
      │
      ▼
COMPOSITE
      │
      ▼
Execution Planner
      │
      ▼
SEQUENTIAL
      │
      ▼
Agent Selector
      │
      ▼
Content Processing
      │
      ▼
Educational
      │
      ▼
Response Aggregator

Example 2

User Query

Upload the presentation, summarize it, and generate an infographic.

Routing Flow 

Content Processing
        │
        ▼
Educational
        │
        ▼
Multimedia

10. Agent Responsibilities
Content Processing Agent

Responsible for:

File upload
OCR
Document parsing
Metadata extraction
Chunk generation
Embedding generation
Vector indexing
Educational Content Generator Agent

Responsible for:

Question answering
Summary generation
Quiz generation
Flashcards
Learning objectives
Assignments
Programming questions
Mathematics solutions
Resource recommendations
Explanations
Multimedia Agent

Responsible for:

Image generation
Audio generation
Video generation
Infographics
Diagrams
Multimedia enhancement
Orchestrator Agent

Responsible for:

Intent detection
Workflow selection
Execution planning
Agent selection
State management
Agent coordination
Response aggregation
Error handling

11. Future Routing Enhancements

The Routing Matrix is designed to evolve with the system.

Future improvements may include:

Parallel workflow execution.
Dynamic workflow optimization.
LLM-based intent detection.
Confidence scoring for routing decisions.
Multi-language routing.
User profile–based routing.
Context-aware execution planning.
Agent health monitoring and failover.
Priority-based request scheduling.
Adaptive workflow optimization.

12. Conclusion

The Routing Matrix serves as the central routing specification for the Orchestrator Agent. It provides a clear mapping from user queries to intents, workflows, execution strategies, and agent selections. By centralizing routing decisions, the Orchestrator remains modular, maintainable, and scalable, allowing future enhancements without requiring major architectural changes.
