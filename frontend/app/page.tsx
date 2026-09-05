"use client";

import { useEffect, useState } from "react";
import ChatPage from "@/components/ChatPage";
import Auth from "@/components/Auth";
import Dashboard from "@/components/Dashboard";
import QuizView from "@/components/QuizView";
import FlashcardsView from "@/components/FlashcardsView";

type Section = "home" | "chat" | "quiz" | "flashcards" | "dashboard" | "auth";

interface QuizFlashcardInitProps {
  launchOrigin?: "home" | "chat";
  initialSubject?: string;
  initialTopic?: string;
  initialDifficulty?: string;
  initialDocumentUploaded?: boolean;
  initialNumQuestions?: number;
  initialNumCards?: number;
  autoStart?: boolean;
}

export default function Home() {
  const [activeSection, setActiveSection] = useState<Section>("home");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [redirectTarget, setRedirectTarget] = useState<Section | null>(null);
  const [authNotice, setAuthNotice] = useState<string | null>(null);
  const [quizInitProps, setQuizInitProps] = useState<QuizFlashcardInitProps>({});
  const [flashcardsInitProps, setFlashcardsInitProps] = useState<QuizFlashcardInitProps>({});

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

  const handleAuthFailure = () => {
    localStorage.removeItem("authToken");
    setIsLoggedIn(false);
    setRedirectTarget(activeSection);
    setAuthNotice("Session expired or unauthorized. Please sign in again.");
    setActiveSection("auth");
  };

  const handleRequireAuth = (target: Section, notice?: string) => {
    setRedirectTarget(target);
    setAuthNotice(notice || "Please sign in or create an account to unlock unlimited access.");
    setActiveSection("auth");
  };

  const navigateToSection = (target: Section) => {
    // Chat, Quiz, and Flashcards are accessible directly for guests up to free trial limits
    if (target === "home" || target === "chat" || target === "quiz" || target === "flashcards") {
      setActiveSection(target);
      return;
    }

    // Auth gating for Performance Dashboard
    if (!isLoggedIn) {
      setRedirectTarget(target);
      setAuthNotice("Please sign in or create an account to access your Performance Dashboard.");
      setActiveSection("auth");
    } else {
      setActiveSection(target);
    }
  };

  const openChat = () => {
    setActiveSection("chat");
  };

  const openQuiz = (props: QuizFlashcardInitProps = {}) => {
    setQuizInitProps({ launchOrigin: "home", ...props });
    setActiveSection("quiz");
  };

  const openFlashcards = (props: QuizFlashcardInitProps = {}) => {
    setFlashcardsInitProps({ launchOrigin: "home", ...props });
    setActiveSection("flashcards");
  };

  // =====================================================
  // Auth Screen
  // =====================================================
  if (activeSection === "auth") {
    return (
      <Auth
        customNotice={authNotice || undefined}
        onCancel={() => {
          setActiveSection(redirectTarget || "home");
          setRedirectTarget(null);
          setAuthNotice(null);
        }}
        onAuthSuccess={() => {
          setIsLoggedIn(true);
          setActiveSection(redirectTarget || "home");
          setRedirectTarget(null);
          setAuthNotice(null);
        }}
      />
    );
  }

  // =====================================================
  // Dashboard Analytics
  // =====================================================
  if (activeSection === "dashboard") {
    return <Dashboard onBack={() => setActiveSection("home")} onAuthFailure={handleAuthFailure} />;
  }

  // =====================================================
  // Quiz
  // =====================================================
  if (activeSection === "quiz") {
    return (
      <QuizView
        initialSubject={quizInitProps.initialSubject || ""}
        initialTopic={quizInitProps.initialTopic}
        initialDifficulty={quizInitProps.initialDifficulty}
        initialDocumentUploaded={quizInitProps.initialDocumentUploaded}
        initialNumQuestions={quizInitProps.initialNumQuestions}
        autoStart={quizInitProps.autoStart}
        onBack={() => {
          setActiveSection(quizInitProps.launchOrigin === "chat" ? "chat" : "home");
          setQuizInitProps({});
        }}
        onAuthFailure={handleAuthFailure}
        onRequireAuth={(msg) => handleRequireAuth("quiz", msg)}
      />
    );
  }

  // =====================================================
  // Flashcards
  // =====================================================
  if (activeSection === "flashcards") {
    return (
      <FlashcardsView
        initialSubject={flashcardsInitProps.initialSubject || ""}
        initialTopic={flashcardsInitProps.initialTopic}
        initialDifficulty={flashcardsInitProps.initialDifficulty}
        initialDocumentUploaded={flashcardsInitProps.initialDocumentUploaded}
        initialNumCards={flashcardsInitProps.initialNumCards}
        autoStart={flashcardsInitProps.autoStart}
        onBack={() => {
          setActiveSection(flashcardsInitProps.launchOrigin === "chat" ? "chat" : "home");
          setFlashcardsInitProps({});
        }}
        onAuthFailure={handleAuthFailure}
        onRequireAuth={(msg) => handleRequireAuth("flashcards", msg)}
      />
    );
  }

  // =====================================================
  // Chat
  // =====================================================
  if (activeSection === "chat") {
    return (
      <ChatPage
        onBack={() => setActiveSection("home")}
        onAuthFailure={handleAuthFailure}
        onRequireAuth={(msg) => handleRequireAuth("chat", msg)}
        onOpenQuiz={openQuiz}
        onOpenFlashcards={openFlashcards}
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
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigateToSection("dashboard")}
            className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-medium hover:bg-slate-800 transition"
          >
            📊 Performance Dashboard
          </button>
          {isLoggedIn ? (
            <button
              onClick={handleLogout}
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-medium hover:bg-slate-800 transition"
            >
              Log Out
            </button>
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
        </div>
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

        {/* Main Options Grid */}
        <div className="mt-14 grid w-full max-w-4xl gap-6 md:grid-cols-3">
          
          {/* Card 1: CHAT */}
          <button
            onClick={openChat}
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
