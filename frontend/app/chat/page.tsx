"use client";

import { useState } from "react";
import ChatSidebar from "@/components/ChatSidebar";
import ChatMessage from "@/components/ChatMessage";

interface ComparisonTableData {
  columns: string[];
  rows: string[][];
}

interface Message {
  role: "user" | "assistant";
  content: string;
  comparison_table?: ComparisonTableData;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);

  const [question, setQuestion] = useState("");

  const [loading, setLoading] = useState(false);

  const [subject, setSubject] = useState("OS");

  const sendMessage = async () => {
    if (!question.trim() || loading) {
      return;
    }

    const userQuestion = question.trim();

    // ------------------------------------------
    // Add user message
    // ------------------------------------------

    const userMessage: Message = {
      role: "user",
      content: userQuestion,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setQuestion("");

    setLoading(true);

    try {
      // ------------------------------------------
      // Call Content Processing Agent
      // ------------------------------------------

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

      const data = await response.json();

      console.log("Backend response:", data);

      // ------------------------------------------
      // Add assistant response
      // ------------------------------------------

      const assistantMessage: Message = {
        role: "assistant",

        content:
          data.answer ||
          data.summary ||
          "I could not generate an answer.",

        comparison_table:
          data.comparison_table,
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);
    } catch (error) {
      console.error(
        "Error communicating with backend:",
        error
      );

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Sorry, I could not connect to the Content Processing Agent.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // ------------------------------------------
  // Handle Enter key
  // ------------------------------------------

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      sendMessage();
    }
  };

  return (
    <main className="flex h-screen bg-slate-950 text-white">

      {/* ======================================
          SIDEBAR
      ====================================== */}

      <ChatSidebar />


      {/* ======================================
          MAIN CHAT AREA
      ====================================== */}

      <section className="flex min-w-0 flex-1 flex-col">

        {/* --------------------------------------
            Header
        -------------------------------------- */}

        <header className="border-b border-slate-800 px-6 py-4">

          <div className="flex items-center justify-between">

            <div>
              <h1 className="text-lg font-semibold">
                Educational AI Tutor
              </h1>

              <p className="text-sm text-slate-400">
                Ask questions about your subject
              </p>
            </div>


            {/* Subject selector */}

            <select
              value={subject}
              onChange={(event) =>
                setSubject(event.target.value)
              }
              className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none"
            >
              <option value="OS">Operating System</option>
              <option value="OOP">Object Oriented Programming</option>
              <option value="CNS">Cryptography and Network Security</option>
              <option value="DBMS">Database Management System</option>
              <option value="SE">Software Engineering</option>
              <option value="AI">Artificial Intelligence</option>
              <option value="ETC">Effective Technical Communication</option>
              <option value="COA">Computer Organization and Architecture</option>
              <option value="DATA STRUCTURE">Data Structure</option>

            </select>

          </div>

        </header>


        {/* ======================================
            MESSAGES
        ====================================== */}

        <div className="flex-1 overflow-y-auto px-6 py-8">

          <div className="mx-auto flex max-w-4xl flex-col gap-6">

            {/* Empty state */}

            {messages.length === 0 && (
              <div className="flex flex-1 flex-col items-center justify-center py-32 text-center">

                <h2 className="text-2xl font-semibold">
                  How can I help you?
                </h2>

                <p className="mt-2 max-w-md text-slate-400">
                  Ask a question about your selected
                  subject.
                </p>

              </div>
            )}


            {/* Messages */}

            {messages.map(
              (message, index) => (
                <ChatMessage
                  key={index}
                  message={message}
                />
              )
            )}


            {/* Loading */}

            {loading && (
              <div className="flex justify-start">

                <div className="rounded-2xl bg-slate-900 px-5 py-4 text-sm text-slate-400">

                  Thinking...

                </div>

              </div>
            )}

          </div>

        </div>


        {/* ======================================
            INPUT
        ====================================== */}

        <div className="border-t border-slate-800 p-4">

          <div className="mx-auto flex max-w-4xl gap-3">

            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your subject..."
              rows={1}
              className="min-h-[52px] flex-1 resize-none rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-slate-500"
            />

            <button
              onClick={sendMessage}
              disabled={
                loading ||
                !question.trim()
              }
              className="rounded-xl bg-white px-5 py-3 font-medium text-black transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Send
            </button>

          </div>

          <p className="mx-auto mt-2 max-w-4xl text-xs text-slate-500">
            Press Enter to send · Shift + Enter for a new line
          </p>

        </div>

      </section>

    </main>
  );
}