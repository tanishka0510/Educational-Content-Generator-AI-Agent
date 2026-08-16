"use client";

import { useEffect, useState } from "react";
import ChatSidebar from "@/components/ChatSidebar";
import ChatMessage from "@/components/ChatMessage";

// =====================================================
// Types
// =====================================================

interface ComparisonTableData {
  columns: string[];
  rows: string[][];
}

interface ChatResponse {
  summary?: string;
  answer?: string;
  comparison_table?: ComparisonTableData;
  learning_objectives?: string[];
  keywords?: string[];
  concepts?: string[];
  difficulty?: string;
  topic?: string;
  intent?: string;
  response_style?: string;
  unit?: string;
  retrieval_score?: number;
  sources?: string[];
}

interface Message {
  role: "user" | "assistant";
  content?: string;
  comparison_table?: ComparisonTableData;
}

interface Chat {
  id: string;
  subject: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

// =====================================================
// Props
// =====================================================

interface ChatPageProps {
  subject: string;
  onBack: () => void;
}

// =====================================================
// Storage Keys
// =====================================================

const STORAGE_KEY =
  "educational-content-generator-chats";

const SUBJECT_STORAGE_KEY =
  "educational-content-generator-selected-subject";

// =====================================================
// Subject Names
// =====================================================

const SUBJECT_NAMES: Record<string, string> = {
  OS: "Operating System",
  DBMS: "Database Management System",
  OOP: "Object Oriented Programming",
  COA: "Computer Organization and Architecture",
  AI: "Artificial Intelligence",
  ETC: "Effective Technical Communication",
  "DATA STRUCTURE": "Data Structure",
  CNS: "Cryptography and Network Security",
  SE: "Software Engineering",
};

// =====================================================
// Default Questions
// =====================================================

const DEFAULT_QUESTIONS: Record<string, string[]> = {
  OS: [
    "Compare Process and Thread",
    "Explain Process",
    "Explain Thread",
  ],

  DBMS: [
    "Compare Primary Key and Foreign Key",
    "Explain Normalization",
    "Explain SQL JOIN",
  ],

  OOP: [
    "Compare Inheritance and Polymorphism",
    "Explain Encapsulation",
    "Explain Abstraction",
  ],

  COA: [
    "Compare RISC and CISC",
    "Explain Cache Memory",
    "Explain Pipelining",
  ],

  AI: [
    "Compare Supervised and Unsupervised Learning",
    "Explain Artificial Neural Network",
    "Explain Machine Learning",
  ],

  ETC: [
    "Compare Formal and Informal Communication",
    "Explain Communication Process",
    "Explain Barriers to Communication",
  ],

  "DATA STRUCTURE": [
    "Compare Array and Linked List",
    "Explain Stack",
    "Explain Binary Search Tree",
  ],

  CNS: [
    "Compare Symmetric and Asymmetric Encryption",
    "Explain RSA Algorithm",
    "Explain Digital Signature",
  ],

  SE: [
    "Compare Waterfall and Agile Model",
    "Explain Software Development Life Cycle",
    "Explain Software Testing",
  ],
};

// =====================================================
// Generate Chat ID
// =====================================================

function generateChatId(): string {
  return (
    Date.now().toString() +
    "-" +
    Math.random().toString(36).substring(2, 9)
  );
}

// =====================================================
// Generate Chat Title
// =====================================================

function generateChatTitle(question: string): string {
  const cleanQuestion = question.trim();

  if (cleanQuestion.length <= 45) {
    return cleanQuestion;
  }

  return cleanQuestion.substring(0, 45) + "...";
}

// =====================================================
// Chat Page
// =====================================================

export default function ChatPage({
  subject,
  onBack,
}: ChatPageProps) {
  // ===================================================
  // Current Question
  // ===================================================

  const [question, setQuestion] = useState<string>("");

  // ===================================================
  // Current Messages
  // ===================================================

  const [messages, setMessages] = useState<Message[]>([]);

  // ===================================================
  // Loading
  // ===================================================

  const [loading, setLoading] = useState<boolean>(false);

  // ===================================================
  // All Saved Chats
  // ===================================================

  const [chats, setChats] = useState<Chat[]>([]);

  // ===================================================
  // Active Chat
  // ===================================================

  const [activeChatId, setActiveChatId] =
    useState<string | null>(null);

  // ===================================================
  // Current Subject Name
  // ===================================================

  const subjectName =
    SUBJECT_NAMES[subject] || subject;

  // ===================================================
  // Current Subject Default Questions
  // ===================================================

  const defaultQuestions =
    DEFAULT_QUESTIONS[subject] || [];

  // ===================================================
  // Load Saved Chats
  // ===================================================

  useEffect(() => {
    try {
      const savedChats =
        localStorage.getItem(STORAGE_KEY);

      if (!savedChats) {
        return;
      }

      const parsedChats: unknown =
        JSON.parse(savedChats);

      if (Array.isArray(parsedChats)) {
        setChats(parsedChats as Chat[]);
      }
    } catch (error) {
      console.error(
        "Could not load saved chats:",
        error
      );
    }
  }, []);

  // ===================================================
  // Save Chats
  // ===================================================

  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(chats)
      );
    } catch (error) {
      console.error(
        "Could not save chats:",
        error
      );
    }
  }, [chats]);

  // ===================================================
  // Save Current Subject
  // ===================================================

  useEffect(() => {
    try {
      localStorage.setItem(
        SUBJECT_STORAGE_KEY,
        subject
      );
    } catch (error) {
      console.error(
        "Could not save selected subject:",
        error
      );
    }
  }, [subject]);

  // ===================================================
  // Create New Chat
  // ===================================================

  const handleNewChat = (): void => {
    setMessages([]);
    setQuestion("");
    setActiveChatId(null);
  };

  // ===================================================
  // Select Existing Chat
  // ===================================================

  const handleSelectChat = (
    chat: Chat
  ): void => {
    /*
     * IMPORTANT:
     *
     * The subject of an existing chat is handled by
     * the parent Home page.
     *
     * ChatPage cannot directly change the parent's
     * subject because subject is now controlled by Home.
     *
     * Therefore, this loads the selected chat only.
     */

    setActiveChatId(chat.id);
    setMessages(chat.messages);
    setQuestion("");
  };

  // ===================================================
  // Send Message
  // ===================================================

  const sendMessage = async (): Promise<void> => {
    if (!question.trim() || loading) {
      return;
    }

    const userQuestion = question.trim();

    setQuestion("");

    // =================================================
    // Add User Message
    // =================================================

    const userMessage: Message = {
      role: "user",
      content: userQuestion,
    };

    const updatedMessages: Message[] = [
      ...messages,
      userMessage,
    ];

    setMessages(updatedMessages);

    setLoading(true);

    try {
      // =================================================
      // Backend Request
      // =================================================

      const response = await fetch(
        "http://127.0.0.1:8000/process-content",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            subject: subject,
            question: userQuestion,
            document_uploaded: false,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Backend error: ${response.status}`
        );
      }

      const data: ChatResponse =
        await response.json();

      console.log(
        "Backend response:",
        data
      );

      // =================================================
      // Assistant Message
      // =================================================

      const assistantMessage: Message = {
        role: "assistant",

        content:
          data.answer ||
          data.summary ||
          "I could not generate an answer.",

        comparison_table:
          data.comparison_table,
      };

      const finalMessages: Message[] = [
        ...updatedMessages,
        assistantMessage,
      ];

      setMessages(finalMessages);

      // =================================================
      // Existing Chat
      // =================================================

      if (activeChatId) {
        setChats(
          (previousChats) =>
            previousChats.map((chat) => {
              if (
                chat.id !== activeChatId
              ) {
                return chat;
              }

              return {
                ...chat,

                subject: subject,

                messages:
                  finalMessages,

                updatedAt:
                  new Date().toISOString(),
              };
            })
        );
      }

      // =================================================
      // New Chat
      // =================================================

      else {
        const newChatId =
          generateChatId();

        const now =
          new Date().toISOString();

        const newChat: Chat = {
          id: newChatId,

          subject: subject,

          title:
            generateChatTitle(
              userQuestion
            ),

          messages:
            finalMessages,

          createdAt: now,

          updatedAt: now,
        };

        setChats(
          (previousChats) => [
            newChat,
            ...previousChats,
          ]
        );

        setActiveChatId(
          newChatId
        );
      }
    } catch (error) {
      console.error(
        "Error communicating with backend:",
        error
      );

      const errorMessage: Message = {
        role: "assistant",

        content:
          "Sorry, I could not connect to the Content Processing Agent.",
      };

      const finalMessages: Message[] = [
        ...updatedMessages,
        errorMessage,
      ];

      setMessages(finalMessages);
    } finally {
      setLoading(false);
    }
  };

  // ===================================================
  // Handle Enter Key
  // ===================================================

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ): void => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      sendMessage();
    }
  };

  // ===================================================
  // Handle Default Question
  // ===================================================

  const handleDefaultQuestion = (
    selectedQuestion: string
  ): void => {
    setQuestion(selectedQuestion);
  };

  // ===================================================
  // Render
  // ===================================================

  return (
    <main className="flex h-screen overflow-hidden bg-slate-950 text-white">

      {/* =================================================
          SIDEBAR
      ================================================= */}

      <ChatSidebar
        chats={chats}
        currentSubject={subject}
        activeChatId={activeChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onBack={onBack}
      />

      {/* =================================================
          MAIN CHAT AREA
      ================================================= */}

      <section className="flex min-w-0 flex-1 flex-col">

        {/* =================================================
            HEADER
        ================================================= */}

        <header className="flex h-16 items-center justify-between border-b border-slate-800 px-6">

          <div>
            <h1 className="font-semibold">
              Educational AI Tutor
            </h1>

            <p className="text-xs text-slate-500">
              Ask questions from your study material
            </p>
          </div>

          {/* =================================================
              SUBJECT SELECTOR
          ================================================= */}

          {/*
            IMPORTANT:

            Subject is controlled by the parent Home page.

            Therefore, the subject selector is intentionally
            removed from ChatPage.

            The selected subject from Home is passed here
            through the "subject" prop.
          */}

          <div className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white">
            {subjectName}
          </div>

        </header>

        {/* =================================================
            MESSAGES
        ================================================= */}

        <div className="flex-1 overflow-y-auto">

          {messages.length === 0 ? (

            // =================================================
            // EMPTY STATE
            // =================================================

            <div className="flex h-full items-center justify-center px-6">

              <div className="max-w-xl text-center">

                <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-800 text-2xl">
                  💬
                </div>

                <h2 className="text-2xl font-semibold">
                  What would you like to learn?
                </h2>

                <p className="mt-3 text-slate-500">
                  Ask a question about{" "}
                  {subjectName}.
                </p>

                {/* =================================================
                    DEFAULT QUESTIONS
                ================================================= */}

                {defaultQuestions.length > 0 && (
                  <div className="mt-6 flex flex-wrap justify-center gap-2">

                    {defaultQuestions.map(
                      (
                        defaultQuestion,
                        index
                      ) => (

                        <button
                          key={index}
                          onClick={() =>
                            handleDefaultQuestion(
                              defaultQuestion
                            )
                          }
                          className="rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-400 transition hover:bg-slate-800 hover:text-white"
                        >
                          {defaultQuestion}
                        </button>

                      )
                    )}

                  </div>
                )}

              </div>

            </div>

          ) : (

            // =================================================
            // CHAT MESSAGES
            // =================================================

            <div className="mx-auto max-w-4xl space-y-8 px-6 py-8">

              {messages.map(
                (
                  message,
                  index
                ) => (

                  <ChatMessage
                    key={index}
                    message={message}
                  />

                )
              )}

              {/* =================================================
                  LOADING
              ================================================= */}

              {loading && (
                <div className="text-sm text-slate-500">
                  Thinking...
                </div>
              )}

            </div>

          )}

        </div>

        {/* =================================================
            INPUT
        ================================================= */}

        <div className="border-t border-slate-800 p-4">

          <div className="mx-auto flex max-w-4xl items-end gap-3 rounded-2xl border border-slate-700 bg-slate-900 p-2">

            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(
                  event.target.value
                )
              }
              onKeyDown={handleKeyDown}
              placeholder={`Ask a question about ${subjectName}...`}
              rows={1}
              className="max-h-32 min-h-12 flex-1 resize-none bg-transparent px-3 py-3 text-sm text-white outline-none placeholder:text-slate-600"
            />

            <button
              onClick={sendMessage}
              disabled={
                !question.trim() ||
                loading
              }
              className="rounded-xl bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-40"
            >
              ↑
            </button>

          </div>

          <p className="mt-2 text-center text-xs text-slate-600">
            Press Enter to send · Shift + Enter for a new line
          </p>

        </div>

      </section>

    </main>
  );
}
