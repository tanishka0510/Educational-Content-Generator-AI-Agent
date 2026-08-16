"use client";

import { useState } from "react";
import ChatPage from "@/components/ChatPage";

type Section = "home" | "chat" | "quiz" | "flashcards";

type Subject ="OS"| "OOP"| "DBMS"| "CNS"| "SE"| "AI"| "ETC"| "COA"| "DATA STRUCTURE";

export default function Home() {
  const [activeSection, setActiveSection] =
    useState<Section>("home");

  const [subject, setSubject] =
    useState<Subject>("OS");

  // =====================================================
  // Open Chat
  // =====================================================

  const openChat = (selectedSubject: Subject) => {
    setSubject(selectedSubject);
    setActiveSection("chat");
  };

  // =====================================================
  // Quiz
  // =====================================================

  if (activeSection === "quiz") {
    return (
      <main className="min-h-screen bg-slate-950 text-white">
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">

            <h1 className="text-3xl font-bold">
              Quiz
            </h1>

            <p className="mt-3 text-slate-400">
              Quiz interface will be built here.
            </p>

            <button
              onClick={() =>
                setActiveSection("home")
              }
              className="mt-6 rounded-lg bg-white px-5 py-2 text-sm font-medium text-slate-950 hover:bg-slate-200"
            >
              Back
            </button>

          </div>
        </div>
      </main>
    );
  }

  // =====================================================
  // Flashcards
  // =====================================================

  if (activeSection === "flashcards") {
    return (
      <main className="min-h-screen bg-slate-950 text-white">
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">

            <h1 className="text-3xl font-bold">
              Flashcards
            </h1>

            <p className="mt-3 text-slate-400">
              Flashcard interface will be built here.
            </p>

            <button
              onClick={() =>
                setActiveSection("home")
              }
              className="mt-6 rounded-lg bg-white px-5 py-2 text-sm font-medium text-slate-950 hover:bg-slate-200"
            >
              Back
            </button>

          </div>
        </div>
      </main>
    );
  }

  // =====================================================
  // Chat
  // =====================================================

  if (activeSection === "chat") {
    return (
      <ChatPage
        subject={subject}
        onBack={() =>
          setActiveSection("home")
        }
      />
    );
  }

  // =====================================================
  // Home Page
  // =====================================================

  return (
    <main className="min-h-screen bg-slate-950 text-white">

      <div className="mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center px-6 py-16">

        {/* Header */}

        <div className="text-center">

          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-slate-400">
            AI Educational Assistant
          </p>

          <h1 className="text-5xl font-bold tracking-tight">
            Educational Content Generator
          </h1>

          <p className="mx-auto mt-5 max-w-2xl text-lg text-slate-400">
            Learn concepts, test your knowledge, and revise
            important topics using AI-powered educational tools.
          </p>

        </div>

        {/* =================================================
            Subject Selection
        ================================================= */}

        <div className="mt-10">

          <label className="mb-2 block text-center text-sm text-slate-400">
            Select Subject
          </label>

          <select
            value={subject}
            onChange={(event) =>
              setSubject(
                event.target.value as Subject
              )
            }
            className="rounded-xl border border-slate-700 bg-slate-900 px-5 py-3 text-white outline-none focus:border-slate-500"
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

        {/* =================================================
            Main Options
        ================================================= */}

        <div className="mt-14 grid w-full max-w-4xl gap-6 md:grid-cols-3">

          {/* =================================================
              CHAT
          ================================================= */}

          <button
            onClick={() =>
              openChat(subject)
            }
            className="group rounded-2xl border border-slate-800 bg-slate-900 p-8 text-left transition hover:-translate-y-1 hover:border-slate-600 hover:bg-slate-800"
          >

            <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800 text-2xl">
              💬
            </div>

            <h2 className="text-xl font-semibold">
              Chat
            </h2>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Ask questions and get educational explanations
              from your subject material.
            </p>

            <div className="mt-6 text-sm font-medium text-white">
              Start chatting →
            </div>

          </button>

          {/* =================================================
              QUIZ
          ================================================= */}

          <button
            onClick={() =>
              setActiveSection("quiz")
            }
            className="group rounded-2xl border border-slate-800 bg-slate-900 p-8 text-left transition hover:-translate-y-1 hover:border-slate-600 hover:bg-slate-800"
          >

            <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800 text-2xl">
              📝
            </div>

            <h2 className="text-xl font-semibold">
              Quiz
            </h2>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Test your understanding with AI-generated
              questions from your study material.
            </p>

            <div className="mt-6 text-sm font-medium text-white">
              Take a quiz →
            </div>

          </button>

          {/* =================================================
              FLASHCARDS
          ================================================= */}

          <button
            onClick={() =>
              setActiveSection("flashcards")
            }
            className="group rounded-2xl border border-slate-800 bg-slate-900 p-8 text-left transition hover:-translate-y-1 hover:border-slate-600 hover:bg-slate-800"
          >

            <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800 text-2xl">
              🎴
            </div>

            <h2 className="text-xl font-semibold">
              Flashcards
            </h2>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Revise important concepts quickly using
              interactive flashcards.
            </p>

            <div className="mt-6 text-sm font-medium text-white">
              Start revision →
            </div>

          </button>

        </div>

      </div>

    </main>
  );
}