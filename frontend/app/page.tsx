"use client";

import { useEffect, useState } from "react";
import ChatPage from "@/components/ChatPage";
import Auth from "@/components/Auth";
import Dashboard from "@/components/Dashboard";
import QuizView from "@/components/QuizView";
import FlashcardsView from "@/components/FlashcardsView";

type Section = "home" | "chat" | "quiz" | "flashcards" | "dashboard" | "auth";

type Subject =
  | "OS"
  | "OOP"
  | "DBMS"
  | "CNS"
  | "SE"
  | "AI"
  | "ETC"
  | "COA"
  | "DATA STRUCTURE";

export default function Home() {
  const [activeSection, setActiveSection] = useState<Section>("home");
  const [subject, setSubject] = useState<Subject>("OS");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [redirectTarget, setRedirectTarget] = useState<Section | null>(null);

  // Check login state on mount
  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    setIsLoggedIn(false);
    setActiveSection("home");
  };

  const navigateToSection = (target: Section) => {
    if (target === "home" || target === "chat") {
      setActiveSection(target);
      return;
    }

    // Auth gating for other sections
    if (!isLoggedIn) {
      setRedirectTarget(target);
      setActiveSection("auth");
    } else {
      setActiveSection(target);
    }
  };

  const openChat = (selectedSubject: Subject) => {
    setSubject(selectedSubject);
    setActiveSection("chat");
  };

  // =====================================================
  // Auth Screen
  // =====================================================
  if (activeSection === "auth") {
    return (
      <Auth
        onAuthSuccess={() => {
          setIsLoggedIn(true);
          setActiveSection(redirectTarget || "home");
          setRedirectTarget(null);
        }}
      />
    );
  }

  // =====================================================
  // Dashboard Analytics
  // =====================================================
  if (activeSection === "dashboard") {
    return <Dashboard onBack={() => setActiveSection("home")} />;
  }

  // =====================================================
  // Quiz
  // =====================================================
  if (activeSection === "quiz") {
    return <QuizView onBack={() => setActiveSection("home")} />;
  }

  // =====================================================
  // Flashcards
  // =====================================================
  if (activeSection === "flashcards") {
    return <FlashcardsView onBack={() => setActiveSection("home")} />;
  }

  // =====================================================
  // Chat
  // =====================================================
  if (activeSection === "chat") {
    return (
      <ChatPage
        subject={subject}
        onBack={() => setActiveSection("home")}
      />
    );
  }

  // =====================================================
  // Home / Landing Page
  // =====================================================
  return (
    <main className="min-h-screen bg-slate-950 text-white relative">
      
      {/* Top Navigation Bar */}
      <nav className="absolute top-0 right-0 p-6 flex justify-end items-center gap-4">
        {isLoggedIn ? (
          <div className="flex items-center gap-4">
            <button
              onClick={() => setActiveSection("dashboard")}
              className="text-sm font-medium text-slate-350 hover:text-white transition"
            >
              📊 Performance Dashboard
            </button>
            <button
              onClick={handleLogout}
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-medium hover:bg-slate-800 transition"
            >
              Log Out
            </button>
          </div>
        ) : (
          <button
            onClick={() => {
              setRedirectTarget("home");
              setActiveSection("auth");
            }}
            className="rounded-xl bg-white px-5 py-2.5 text-sm font-semibold text-slate-950 hover:bg-slate-200 transition"
          >
            Sign In
          </button>
        )}
      </nav>

      <div className="mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center px-6 py-16">
        
        {/* Header Title */}
        <div className="text-center mt-12">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-slate-400">
            AI Educational Assistant
          </p>
          <h1 className="text-5xl font-bold tracking-tight">
            Educational Content Generator
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-slate-400">
            Learn concepts, test your knowledge, and revise important topics using
            AI-powered multi-agent learning tools.
          </p>
        </div>

        {/* Subject Selection dropdown */}
        <div className="mt-10">
          <label className="mb-2 block text-center text-sm text-slate-400">
            Select Subject
          </label>
          <select
            value={subject}
            onChange={(event) => setSubject(event.target.value as Subject)}
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

        {/* Main Options Grid */}
        <div className="mt-14 grid w-full max-w-4xl gap-6 md:grid-cols-3">
          
          {/* Card 1: CHAT */}
          <button
            onClick={() => openChat(subject)}
            className="group rounded-2xl border border-slate-800 bg-slate-900 p-8 text-left transition hover:-translate-y-1 hover:border-slate-600 hover:bg-slate-800"
          >
            <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800 text-2xl">
              💬
            </div>
            <h2 className="text-xl font-semibold">Chat Assistant</h2>
            <p className="mt-3 text-sm leading-6 text-slate-400 font-normal">
              Ask questions and get explanations from your subject material or
              uploaded documents.
            </p>
            <div className="mt-6 text-sm font-medium text-white">
              Start chatting →
            </div>
          </button>

          {/* Card 2: QUIZ */}
          <button
            onClick={() => navigateToSection("quiz")}
            className="group rounded-2xl border border-slate-800 bg-slate-900 p-8 text-left transition hover:-translate-y-1 hover:border-slate-600 hover:bg-slate-800"
          >
            <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800 text-2xl">
              📝
            </div>
            <h2 className="text-xl font-semibold">Interactive Quizzes</h2>
            <p className="mt-3 text-sm leading-6 text-slate-400 font-normal">
              Test your understanding with AI-generated questions from your study material.
            </p>
            <div className="mt-6 text-sm font-medium text-white">
              Take a quiz →
            </div>
          </button>

          {/* Card 3: FLASHCARDS */}
          <button
            onClick={() => navigateToSection("flashcards")}
            className="group rounded-2xl border border-slate-800 bg-slate-900 p-8 text-left transition hover:-translate-y-1 hover:border-slate-600 hover:bg-slate-800"
          >
            <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800 text-2xl">
              🎴
            </div>
            <h2 className="text-xl font-semibold">Spaced Flashcards</h2>
            <p className="mt-3 text-sm leading-6 text-slate-400 font-normal">
              Revise important concepts quickly using interactive active-recall flashcards.
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