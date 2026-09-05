"use client";

import { useEffect, useState } from "react";
import LandingPage from "@/components/LandingPage";
import ChatPage from "@/components/ChatPage";
import Auth from "@/components/Auth";
import Dashboard from "@/components/Dashboard";
import QuizView from "@/components/QuizView";
import FlashcardsView from "@/components/FlashcardsView";

type Section = "landing" | "home" | "chat" | "quiz" | "flashcards" | "dashboard" | "auth";

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
  const [activeSection, setActiveSection] = useState<Section>("landing");
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
    setActiveSection("landing");
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
    // Landing, Home, Chat, Quiz, and Flashcards are accessible directly for guests up to free trial limits
    if (
      target === "landing" ||
      target === "home" ||
      target === "chat" ||
      target === "quiz" ||
      target === "flashcards"
    ) {
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
  // Landing Page (Main Page)
  // =====================================================
  if (activeSection === "landing") {
    return (
      <LandingPage
        onEnterWorkspace={() => setActiveSection("home")}
        onOpenDashboard={() => navigateToSection("dashboard")}
        onSignIn={() => {
          setRedirectTarget("landing");
          setActiveSection("auth");
        }}
        isLoggedIn={isLoggedIn}
        onLogout={handleLogout}
      />
    );
  }

  // =====================================================
  // Auth Screen
  // =====================================================
  if (activeSection === "auth") {
    return (
      <Auth
        customNotice={authNotice || undefined}
        onCancel={() => {
          setActiveSection(redirectTarget || "landing");
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
  // Agent Workspace Hub (The 3 Agents & All Content)
  // =====================================================
  return (
    <main className="min-h-screen bg-[#F8FAFC] text-slate-900 relative flex flex-col font-sans">
      {/* Top Navigation Bar (Crisp White Theme) */}
      <header className="fixed top-0 left-0 right-0 z-40 w-full border-b border-slate-200 bg-white/95 backdrop-blur-md shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setActiveSection("landing")}
              className="group inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs sm:text-sm font-medium text-slate-700 hover:border-slate-400 hover:bg-slate-50 transition shadow-sm"
              title="Return to Home"
            >
              <span className="transition-transform group-hover:-translate-x-1">←</span>
              <span>Home</span>
            </button>
            <span className="hidden sm:inline text-slate-300">|</span>
            <div className="hidden sm:flex items-center gap-2 text-xs text-[#C59B27] font-semibold tracking-wide uppercase">
              <span className="flex h-2 w-2 rounded-full bg-[#C59B27] animate-pulse"></span>
              <span>Autonomous Agent Workspace</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigateToSection("dashboard")}
              className="rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs sm:text-sm font-medium text-slate-700 hover:bg-slate-50 transition shadow-sm"
            >
              📊 Performance Dashboard
            </button>
            {isLoggedIn ? (
              <button
                onClick={handleLogout}
                className="rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs sm:text-sm font-medium text-slate-700 hover:bg-slate-50 transition shadow-sm"
              >
                Log Out
              </button>
            ) : (
              <button
                onClick={() => {
                  setRedirectTarget("home");
                  setActiveSection("auth");
                }}
                className="rounded-lg bg-[#C59B27] hover:bg-[#B38A1F] px-4 py-2 text-xs sm:text-sm font-semibold text-white shadow-md transition"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="mx-auto flex flex-1 w-full max-w-6xl flex-col items-center justify-center px-6 pt-28 pb-16">
        {/* Header Title */}
        <div className="text-center max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-[#C59B27]/30 bg-amber-50 px-4 py-1 text-xs font-semibold text-[#C59B27] mb-4 shadow-sm">
            <span>✨ Autonomous Multi-Agent Learning Suite</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-serif font-normal tracking-tight text-slate-900">
            Educational Content Generator
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-base sm:text-lg text-slate-600 font-normal leading-relaxed">
            Select a specialized AI agent tool below to chat with your study materials, test your understanding
            with adaptive quizzes, or reinforce key concepts with active-recall flashcards.
          </p>
        </div>

        {/* Main Options Grid */}
        <div className="mt-12 grid w-full max-w-5xl gap-6 md:grid-cols-3">
          {/* Card 1: CHAT */}
          <button
            onClick={openChat}
            className="group relative flex flex-col justify-between rounded-2xl border border-slate-200/80 bg-white p-8 text-left transition-all hover:-translate-y-1.5 hover:border-[#C59B27] hover:shadow-xl hover:shadow-[#C59B27]/10 shadow-sm"
          >
            <div>
              <div className="mb-6 flex items-center justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-50 border border-[#C59B27]/30 text-2xl text-[#C59B27] group-hover:scale-110 transition-transform">
                  💬
                </div>
                <span className="rounded-md border border-[#C59B27]/30 bg-amber-50 px-2.5 py-1 text-[11px] font-semibold text-[#C59B27]">
                  3 Agents Coordinated
                </span>
              </div>
              <h2 className="text-xl font-serif font-bold text-slate-900">Chat Assistant</h2>
              <p className="mt-3 text-sm leading-6 text-slate-600 font-normal">
                Ask questions and get explanations from your subject material or uploaded documents with voice responses and diagram generation.
              </p>
            </div>
            <div className="mt-8 flex items-center gap-2 text-sm font-semibold text-[#C59B27] group-hover:text-[#B38A1F]">
              <span>Start chatting</span>
              <span className="transition-transform group-hover:translate-x-1">→</span>
            </div>
          </button>

          {/* Card 2: QUIZ */}
          <button
            onClick={() => navigateToSection("quiz")}
            className="group relative flex flex-col justify-between rounded-2xl border border-slate-200/80 bg-white p-8 text-left transition-all hover:-translate-y-1.5 hover:border-[#C59B27] hover:shadow-xl hover:shadow-[#C59B27]/10 shadow-sm"
          >
            <div>
              <div className="mb-6 flex items-center justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-50 border border-[#C59B27]/30 text-2xl text-[#C59B27] group-hover:scale-110 transition-transform">
                  📝
                </div>
                <span className="rounded-md border border-[#C59B27]/30 bg-amber-50 px-2.5 py-1 text-[11px] font-semibold text-[#C59B27]">
                  Pedagogical Engine
                </span>
              </div>
              <h2 className="text-xl font-serif font-bold text-slate-900">Interactive Quizzes</h2>
              <p className="mt-3 text-sm leading-6 text-slate-600 font-normal">
                Test your understanding with AI-generated questions from your study material or any academic subject with instant rationales.
              </p>
            </div>
            <div className="mt-8 flex items-center gap-2 text-sm font-semibold text-[#C59B27] group-hover:text-[#B38A1F]">
              <span>Take a quiz</span>
              <span className="transition-transform group-hover:translate-x-1">→</span>
            </div>
          </button>

          {/* Card 3: FLASHCARDS */}
          <button
            onClick={() => navigateToSection("flashcards")}
            className="group relative flex flex-col justify-between rounded-2xl border border-slate-200/80 bg-white p-8 text-left transition-all hover:-translate-y-1.5 hover:border-[#C59B27] hover:shadow-xl hover:shadow-[#C59B27]/10 shadow-sm"
          >
            <div>
              <div className="mb-6 flex items-center justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-50 border border-[#C59B27]/30 text-2xl text-[#C59B27] group-hover:scale-110 transition-transform">
                  🎴
                </div>
                <span className="rounded-md border border-[#C59B27]/30 bg-amber-50 px-2.5 py-1 text-[11px] font-semibold text-[#C59B27]">
                  Spaced Repetition
                </span>
              </div>
              <h2 className="text-xl font-serif font-bold text-slate-900">Spaced Flashcards</h2>
              <p className="mt-3 text-sm leading-6 text-slate-600 font-normal">
                Revise important concepts quickly using interactive active-recall flashcards with spaced repetition ratings and mastery scoring.
              </p>
            </div>
            <div className="mt-8 flex items-center gap-2 text-sm font-semibold text-[#C59B27] group-hover:text-[#B38A1F]">
              <span>Start revision</span>
              <span className="transition-transform group-hover:translate-x-1">→</span>
            </div>
          </button>
        </div>
      </div>
    </main>
  );
}
