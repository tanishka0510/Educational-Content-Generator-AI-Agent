"use client";

import { useState } from "react";
import Image from "next/image";

interface LandingPageProps {
  onEnterWorkspace: () => void;
  onOpenDashboard: () => void;
  onSignIn: () => void;
  isLoggedIn: boolean;
  onLogout: () => void;
}

export default function LandingPage({
  onEnterWorkspace,
  onOpenDashboard,
  onSignIn,
  isLoggedIn,
  onLogout,
}: LandingPageProps) {
  const [openFaqIndex, setOpenFaqIndex] = useState<number | null>(null);
  const [quickTopic, setQuickTopic] = useState("");
  const [quickGoal, setQuickGoal] = useState("Exam Preparation");

  const toggleFaq = (index: number) => {
    setOpenFaqIndex(openFaqIndex === index ? null : index);
  };

  const handleQuickStart = (e: React.FormEvent) => {
    e.preventDefault();
    onEnterWorkspace();
  };

  const targetAudiences = [
    {
      title: "Students & Exam Candidates",
      icon: "🎓",
      tagline: "Ace exams with half the study time",
      description:
        "Ingest dense textbooks, research articles, and lecture slides. Generate diagnostic quizzes and active-recall flashcards before tests to solidify retention and eliminate blindspots.",
      features: [
        "Instant quiz generation from past papers",
        "Active recall flashcards for fast revision",
        "Topic breakdown with difficulty progression",
      ],
    },
    {
      title: "Educators & Course Creators",
      icon: "👩‍🏫",
      tagline: "Automate curriculum & assessment creation",
      description:
        "Turn raw syllabus documents or lesson notes into comprehensive pedagogical assets: multi-level quizzes with rationales, study plans, summary cheat-sheets, and audio lesson recaps.",
      features: [
        "Automated question banks with answer keys",
        "Structured study schedules for syllabus completion",
        "Comparison matrices for difficult concepts",
      ],
    },
    {
      title: "Software Engineers & Tech Learners",
      icon: "💻",
      tagline: "Master code, architectures & math",
      description:
        "Break down complex technical documentation, API specifications, and algorithmic concepts with syntax-highlighted code explanations and structured architectural comparisons.",
      features: [
        "Code walkthroughs with inline commentary",
        "Framework & architecture comparison tables",
        "Mathematical and algorithmic step-by-step proofs",
      ],
    },
    {
      title: "Researchers & Lifelong Learners",
      icon: "🔬",
      tagline: "Synthesize papers & listen on the go",
      description:
        "Digest heavy academic papers, whitepapers, and industry reports. Generate voice summaries and podcasts to learn while walking, commuting, or working out.",
      features: [
        "Dense document summarization with citations",
        "Audio podcasts synthesized from papers",
        "Key takeaways and research objective extraction",
      ],
    },
  ];

  const faqs = [
    {
      q: "What makes SmartLearn different from a standard AI chatbot?",
      a: "Standard chatbots use a single prompt-response loop without specialized cognitive grounding. SmartLearn deploys a coordinated Multi-Agent Architecture: the Content Processing Agent embeds and verifies your documents, the Educational Content Generator enforces proven pedagogical strategies (quizzes, flashcards, study plans), and the Multimedia Agent produces voice synthesis and diagrams—all managed by an autonomous Orchestrator.",
    },
    {
      q: "What file formats can I upload to study?",
      a: "You can upload PDF files, Microsoft Word (.docx), plain text (.txt), and markdown files. The Content Processing Agent automatically extracts the text, segments it into semantic chunks, and creates vector embeddings for instant querying.",
    },
    {
      q: "Can I use the platform without uploading documents?",
      a: "Yes! You can choose any topic, subject, or academic discipline (Computer Science, Biology, History, Physics, Mathematics, etc.) and the agents will synthesize comprehensive educational materials directly from domain knowledge.",
    },
    {
      q: "How does the active recall quiz and flashcard system work?",
      a: "When you take a quiz or review flashcards, the system tracks your accuracy, difficulty level, and mastery history. You receive instant explanations for incorrect answers, and flashcards follow spaced repetition principles so you focus on concepts that need the most practice.",
    },
    {
      q: "Is my progress saved?",
      a: "Yes! When signed in, all your chat conversations, quiz scores, flashcard decks, and subject mastery analytics are saved and visualized in your personal Performance Dashboard.",
    },
    {
      q: "How do I get started?",
      a: "Click the 'Launch Workspace' button in the navigation bar or anywhere on this page. You will be taken immediately into the workspace containing the three agents and all the tools to chat, take quizzes, or generate flashcards!",
    },
  ];

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 font-sans selection:bg-[#C59B27] selection:text-white relative">
      
      {/* =====================================================
          1. FIXED TOP NAVBAR (Matching PROSPERUM reference)
      ====================================================== */}
      <header className="fixed top-0 left-0 right-0 z-50 w-full bg-[#0B1220]/95 backdrop-blur-md border-b border-white/10 shadow-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          
          {/* Brand Logo with Gold Emblem */}
          <div
            className="flex items-center gap-3 cursor-pointer"
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-full border-2 border-[#C59B27] bg-[#C59B27]/10 shadow-sm text-[#C59B27] font-serif font-bold text-base">
              SL
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-serif font-bold tracking-wider text-white uppercase">
                  SmartLearn
                </span>
              </div>
              <p className="text-[10px] tracking-widest text-[#D4AF37] font-semibold uppercase">
                Autonomous Learning Suite
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <a href="#about" className="hover:text-white transition-colors">About</a>
            <a href="#solutions" className="hover:text-white transition-colors">Solutions</a>
            <a href="#audience" className="hover:text-white transition-colors">Whom to Use</a>
            <a href="#how-it-works" className="hover:text-white transition-colors">How We Work</a>
            <a href="#faq" className="hover:text-white transition-colors">FAQ</a>
          </nav>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            <button
              onClick={onOpenDashboard}
              className="hidden sm:flex items-center gap-1.5 rounded-lg border border-white/15 bg-white/5 px-3.5 py-2 text-xs font-medium text-slate-200 hover:bg-white/10 transition"
              title="Open Performance Dashboard"
            >
              <span>📊</span>
              <span>Dashboard</span>
            </button>

            {isLoggedIn ? (
              <button
                onClick={onLogout}
                className="rounded-lg border border-white/15 bg-white/5 px-3.5 py-2 text-xs font-medium text-slate-200 hover:bg-white/10 transition"
              >
                Log Out
              </button>
            ) : (
              <button
                onClick={onSignIn}
                className="rounded-lg border border-white/15 bg-white/5 px-3.5 py-2 text-xs font-medium text-slate-200 hover:bg-white/10 transition"
              >
                Sign In
              </button>
            )}

            {/* Gold Accent CTA Button (Exact styling from PROSPERUM) */}
            <button
              id="launch-workspace-navbar-btn"
              onClick={onEnterWorkspace}
              className="rounded-lg bg-[#C59B27] hover:bg-[#B38A1F] px-5 py-2.5 text-xs sm:text-sm font-semibold text-white shadow-md transition-all hover:shadow-lg active:scale-98"
            >
              Launch Workspace
            </button>
          </div>

        </div>
      </header>

      {/* =====================================================
          2. HERO SECTION (Dark Navy with Grand Campus Background)
      ====================================================== */}
      <section className="relative pt-32 pb-28 md:pt-40 md:pb-36 px-6 overflow-hidden bg-[#0B1220]">
        
        {/* Background Image: Historic Collegiate Campus with Deep Navy Overlay */}
        <div className="absolute inset-0 z-0">
          <div
            className="w-full h-full bg-cover bg-center"
            style={{
              backgroundImage: "url('/images/campus-historic.jpg')",
            }}
          />
          {/* Deep atmospheric navy gradient overlay for readability and exact PROSPERUM aesthetic */}
          <div className="absolute inset-0 bg-gradient-to-r from-[#0B1220] via-[#0B1220]/90 to-[#0B1220]/75" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0B1220] via-transparent to-[#0B1220]/60" />
        </div>

        <div className="relative z-10 mx-auto max-w-7xl">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Content Column */}
            <div className="lg:col-span-7">
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-serif font-normal text-white leading-[1.15] tracking-tight">
                Achieve Academic Success & Subject Mastery
              </h1>

              <p className="mt-6 max-w-2xl text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
                Expert pedagogical AI planning and autonomous multi-agent learning solutions tailored for your coursework, exams, and research.
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-4">
                <button
                  id="launch-workspace-hero-btn"
                  onClick={onEnterWorkspace}
                  className="rounded-lg bg-[#C59B27] hover:bg-[#B38A1F] px-8 py-3.5 text-sm sm:text-base font-semibold text-white shadow-lg transition-all hover:scale-[1.02] active:scale-[0.98]"
                >
                  Launch Workspace
                </button>

                <a
                  href="#about"
                  className="rounded-lg border border-white/20 bg-white/5 hover:bg-white/10 px-6 py-3.5 text-sm sm:text-base font-medium text-white transition-all backdrop-blur-sm"
                >
                  Learn More
                </a>
              </div>
            </div>

            {/* Right Column: 3 Floating Accent Cards (Exact Match to Mockup!) */}
            <div className="lg:col-span-5 flex items-center justify-center lg:justify-end">
              <div className="flex items-center gap-4">
                
                {/* Floating Card 1: Navy with Upward Arrow */}
                <div className="flex flex-col items-center justify-center h-24 w-24 sm:h-28 sm:w-28 rounded-2xl bg-[#14223D]/90 border border-white/15 backdrop-blur-md shadow-2xl transition hover:-translate-y-1">
                  <span className="text-3xl text-white font-bold mb-1">↗</span>
                  <span className="text-[10px] text-slate-300 uppercase tracking-widest font-semibold">Recall</span>
                </div>

                {/* Floating Card 2: Warm Gold with Users/Agent Icon */}
                <div className="flex flex-col items-center justify-center h-28 w-28 sm:h-32 sm:w-32 rounded-2xl bg-[#C59B27] border border-[#E0A96D] shadow-2xl transition hover:-translate-y-1 -translate-y-2">
                  <span className="text-4xl text-white mb-1">👥</span>
                  <span className="text-[10px] text-white uppercase tracking-widest font-bold">3 Agents</span>
                </div>

                {/* Floating Card 3: Deep Navy with Shield Icon */}
                <div className="flex flex-col items-center justify-center h-24 w-24 sm:h-28 sm:w-28 rounded-2xl bg-[#14223D]/90 border border-white/15 backdrop-blur-md shadow-2xl transition hover:-translate-y-1">
                  <span className="text-3xl text-white font-bold mb-1">🛡️</span>
                  <span className="text-[10px] text-slate-300 uppercase tracking-widest font-semibold">Grounded</span>
                </div>

              </div>
            </div>

          </div>
        </div>
      </section>

      {/* =====================================================
          3. THREE OVERLAPPING WHITE FEATURE CARDS
          (Sitting right on the seam between hero and body)
      ====================================================== */}
      <section className="relative z-20 -mt-14 md:-mt-18 px-6">
        <div className="mx-auto max-w-7xl">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Overlapping Card 1: Knowledge Building */}
            <div className="rounded-2xl bg-white p-7 sm:p-8 shadow-[0_15px_35px_-5px_rgba(0,0,0,0.08)] border border-slate-100 transition-all hover:-translate-y-1.5 hover:shadow-[0_20px_40px_-5px_rgba(0,0,0,0.12)]">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 text-slate-800 text-xl font-bold">
                  📊
                </div>
                <h3 className="text-lg font-bold text-slate-900">Knowledge Ingestion</h3>
              </div>
              <p className="text-sm text-slate-600 leading-relaxed min-h-[48px]">
                Deep semantic vector chunking for PDFs, lecture notes, and textbooks with 100% verifiable citations.
              </p>
              <div className="mt-6 pt-4 border-t border-slate-100">
                <button
                  onClick={onEnterWorkspace}
                  className="text-xs font-semibold text-[#C59B27] hover:text-[#9F7B18] transition inline-flex items-center gap-1"
                >
                  <span>Discover More</span>
                  <span>→</span>
                </button>
              </div>
            </div>

            {/* Overlapping Card 2: Adaptive Growth */}
            <div className="rounded-2xl bg-white p-7 sm:p-8 shadow-[0_15px_35px_-5px_rgba(0,0,0,0.08)] border border-slate-100 transition-all hover:-translate-y-1.5 hover:shadow-[0_20px_40px_-5px_rgba(0,0,0,0.12)]">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-50 text-[#C59B27] text-xl font-bold">
                  🧠
                </div>
                <h3 className="text-lg font-bold text-slate-900">Adaptive Diagnostic Quizzes</h3>
              </div>
              <p className="text-sm text-slate-600 leading-relaxed min-h-[48px]">
                Test your understanding with auto-generated multi-level questions and instant pedagogical explanations.
              </p>
              <div className="mt-6 pt-4 border-t border-slate-100">
                <button
                  onClick={onEnterWorkspace}
                  className="text-xs font-semibold text-[#C59B27] hover:text-[#9F7B18] transition inline-flex items-center gap-1"
                >
                  <span>Discover More</span>
                  <span>→</span>
                </button>
              </div>
            </div>

            {/* Overlapping Card 3: Memory Retention */}
            <div className="rounded-2xl bg-white p-7 sm:p-8 shadow-[0_15px_35px_-5px_rgba(0,0,0,0.08)] border border-slate-100 transition-all hover:-translate-y-1.5 hover:shadow-[0_20px_40px_-5px_rgba(0,0,0,0.12)]">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 text-slate-800 text-xl font-bold">
                  🛡️
                </div>
                <h3 className="text-lg font-bold text-slate-900">Spaced Active Recall</h3>
              </div>
              <p className="text-sm text-slate-600 leading-relaxed min-h-[48px]">
                Solidify exam retention with active-recall flashcard decks aligned with cognitive spaced repetition science.
              </p>
              <div className="mt-6 pt-4 border-t border-slate-100">
                <button
                  onClick={onEnterWorkspace}
                  className="text-xs font-semibold text-[#C59B27] hover:text-[#9F7B18] transition inline-flex items-center gap-1"
                >
                  <span>Discover More</span>
                  <span>→</span>
                </button>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* =====================================================
          4. "OUR EDUCATIONAL SOLUTIONS"
          (Exact replica of "Our Financial Solutions" row)
      ====================================================== */}
      <section id="solutions" className="py-24 px-6">
        <div className="mx-auto max-w-7xl">
          
          <div className="mb-14">
            <h2 className="text-3xl sm:text-4xl font-serif font-bold text-slate-900 tracking-tight">
              Our Educational Solutions
            </h2>
            <p className="mt-3 text-base text-slate-600 max-w-2xl">
              Coordinated learning workflows powered by autonomous AI agents to transform how you study and retain knowledge.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* Card 1: Conversational Tutoring */}
            <div className="rounded-2xl bg-white border border-slate-100 overflow-hidden shadow-[0_10px_30px_-5px_rgba(0,0,0,0.06)] transition-all hover:-translate-y-1.5 hover:shadow-[0_15px_35px_-5px_rgba(0,0,0,0.1)] flex flex-col justify-between">
              <div>
                <div className="relative h-56 w-full overflow-hidden bg-slate-100">
                  <img
                    src="/images/library-study.jpg"
                    alt="University Library Study"
                    className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                  />
                  {/* Floating Circular Emblem (Deep Navy) */}
                  <div className="absolute -bottom-5 right-6 flex h-12 w-12 items-center justify-center rounded-full bg-[#0B1220] border-2 border-white shadow-md text-white text-lg">
                    💬
                  </div>
                </div>
                
                <div className="p-7 pt-9">
                  <h3 className="text-xl font-serif font-bold text-slate-900 mb-2">
                    Socratic Chat Tutoring
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed font-normal">
                    Engage in multi-turn educational dialogues grounded strictly in your syllabus with instant citations and code walkthroughs.
                  </p>
                </div>
              </div>

              <div className="px-7 pb-7">
                <button
                  onClick={onEnterWorkspace}
                  className="w-full rounded-lg bg-[#C59B27] hover:bg-[#B38A1F] py-3 text-xs sm:text-sm font-semibold text-white shadow-sm transition"
                >
                  Learn More
                </button>
              </div>
            </div>

            {/* Card 2: Collaborative Study (Featuring User's Students Image!) */}
            <div className="rounded-2xl bg-white border border-slate-100 overflow-hidden shadow-[0_10px_30px_-5px_rgba(0,0,0,0.06)] transition-all hover:-translate-y-1.5 hover:shadow-[0_15px_35px_-5px_rgba(0,0,0,0.1)] flex flex-col justify-between">
              <div>
                <div className="relative h-56 w-full overflow-hidden bg-slate-100">
                  <img
                    src="/images/students-studying.jpg"
                    alt="Students Collaborative Study"
                    className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                  />
                  {/* Floating Circular Emblem (Warm Gold) */}
                  <div className="absolute -bottom-5 right-6 flex h-12 w-12 items-center justify-center rounded-full bg-[#C59B27] border-2 border-white shadow-md text-white text-lg">
                    🎓
                  </div>
                </div>
                
                <div className="p-7 pt-9">
                  <h3 className="text-xl font-serif font-bold text-slate-900 mb-2">
                    Diagnostic Quizzes & Exams
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed font-normal">
                    Generate multi-difficulty practice tests directly from lecture slides, past exams, or topic outlines with comprehensive rationales.
                  </p>
                </div>
              </div>

              <div className="px-7 pb-7">
                <button
                  onClick={onEnterWorkspace}
                  className="w-full rounded-lg bg-[#C59B27] hover:bg-[#B38A1F] py-3 text-xs sm:text-sm font-semibold text-white shadow-sm transition"
                >
                  Learn More
                </button>
              </div>
            </div>

            {/* Card 3: Multimodal Voice & Audio */}
            <div className="rounded-2xl bg-white border border-slate-100 overflow-hidden shadow-[0_10px_30px_-5px_rgba(0,0,0,0.06)] transition-all hover:-translate-y-1.5 hover:shadow-[0_15px_35px_-5px_rgba(0,0,0,0.1)] flex flex-col justify-between">
              <div>
                <div className="relative h-56 w-full overflow-hidden bg-slate-100">
                  <img
                    src="/images/digital-learning.jpg"
                    alt="Digital & Audio Learning"
                    className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                  />
                  {/* Floating Circular Emblem (Deep Navy) */}
                  <div className="absolute -bottom-5 right-6 flex h-12 w-12 items-center justify-center rounded-full bg-[#0B1220] border-2 border-white shadow-md text-white text-lg">
                    🎙️
                  </div>
                </div>
                
                <div className="p-7 pt-9">
                  <h3 className="text-xl font-serif font-bold text-slate-900 mb-2">
                    Multimodal Voice & Audio
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed font-normal">
                    Convert complex subject answers into studio-quality podcast audio lessons and illustrative conceptual diagrams.
                  </p>
                </div>
              </div>

              <div className="px-7 pb-7">
                <button
                  onClick={onEnterWorkspace}
                  className="w-full rounded-lg bg-[#C59B27] hover:bg-[#B38A1F] py-3 text-xs sm:text-sm font-semibold text-white shadow-sm transition"
                >
                  Learn More
                </button>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* =====================================================
          5. "HOW WE WORK" + "START YOUR SESSION" SPLIT
          (Exact replica of "How We Work" & "Schedule Consultation" Box)
      ====================================================== */}
      <section id="how-it-works" className="py-20 px-6 bg-slate-50 border-t border-slate-200/60">
        <div className="mx-auto max-w-7xl">
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
            
            {/* Left Column: How We Work Process Stepper */}
            <div className="lg:col-span-7">
              <h2 className="text-3xl sm:text-4xl font-serif font-bold text-slate-900 tracking-tight">
                How We Work
              </h2>
              <p className="mt-4 text-base text-slate-600 leading-relaxed max-w-xl">
                A seamless, multi-agent cognitive pipeline designed to convert raw educational materials into deep, permanent knowledge mastery.
              </p>

              {/* Stepper with circular badges and connector lines */}
              <div className="mt-12 space-y-8 relative">
                
                {/* Step 1 */}
                <div className="flex items-start gap-5">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-white border-2 border-[#C59B27] text-[#C59B27] font-bold shadow-sm text-lg">
                    01
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">Ingest Study Materials</h3>
                    <p className="mt-1 text-sm text-slate-600 leading-relaxed">
                      Upload your lecture slides, PDF textbooks, or research papers. Or simply specify any academic topic.
                    </p>
                  </div>
                </div>

                {/* Step 2 */}
                <div className="flex items-start gap-5">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-white border-2 border-[#0B1220] text-[#0B1220] font-bold shadow-sm text-lg">
                    02
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">Autonomous Orchestration</h3>
                    <p className="mt-1 text-sm text-slate-600 leading-relaxed">
                      The Orchestrator Agent analyzes your intent and triggers Content Processing, Educational, and Multimedia Agents in optimal sequence.
                    </p>
                  </div>
                </div>

                {/* Step 3 */}
                <div className="flex items-start gap-5">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-white border-2 border-[#C59B27] text-[#C59B27] font-bold shadow-sm text-lg">
                    03
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">Multi-Agent Synthesis</h3>
                    <p className="mt-1 text-sm text-slate-600 leading-relaxed">
                      Semantic vector search grounds facts, the educational engine drafts tests & flashcards, and audio speech is synthesized.
                    </p>
                  </div>
                </div>

                {/* Step 4 */}
                <div className="flex items-start gap-5">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-white border-2 border-[#0B1220] text-[#0B1220] font-bold shadow-sm text-lg">
                    04
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">Active Mastery & Tracking</h3>
                    <p className="mt-1 text-sm text-slate-600 leading-relaxed">
                      Take interactive quizzes, flip spaced flashcards, and monitor your weakness analytics in the Performance Dashboard.
                    </p>
                  </div>
                </div>

              </div>
            </div>

            {/* Right Column: Deep Navy Consultation / Quick-Start Card (Matching Mockup!) */}
            <div className="lg:col-span-5 rounded-3xl bg-[#0B1220] p-8 sm:p-10 shadow-2xl text-white border border-white/10 relative overflow-hidden">
              <div className="relative z-10">
                <h3 className="text-2xl sm:text-3xl font-serif font-normal text-white">
                  Start Your Free Learning Session
                </h3>
                <p className="mt-3 text-xs sm:text-sm text-slate-300 leading-relaxed">
                  Enter your subject or learning objective to instantly configure the multi-agent workspace.
                </p>

                <form onSubmit={handleQuickStart} className="mt-8 space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                      Subject or Topic
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Operating Systems, Quantum Physics, Java"
                      value={quickTopic}
                      onChange={(e) => setQuickTopic(e.target.value)}
                      className="w-full rounded-lg border border-white/15 bg-white/5 px-4 py-3 text-sm text-white placeholder-slate-400 focus:border-[#C59B27] focus:outline-none focus:ring-1 focus:ring-[#C59B27] transition"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                      Primary Learning Goal
                    </label>
                    <select
                      value={quickGoal}
                      onChange={(e) => setQuickGoal(e.target.value)}
                      className="w-full rounded-lg border border-white/15 bg-[#14223D] px-4 py-3 text-sm text-white focus:border-[#C59B27] focus:outline-none focus:ring-1 focus:ring-[#C59B27] transition"
                    >
                      <option value="Exam Preparation">Exam Preparation & Practice Tests</option>
                      <option value="Quick Revision">Quick Revision with Active Flashcards</option>
                      <option value="Socratic Chat">Socratic Question Answering & Notes</option>
                      <option value="Audio Learning">Audio Lessons & Podcasts</option>
                    </select>
                  </div>

                  <div className="pt-2">
                    <button
                      type="submit"
                      className="w-full rounded-lg bg-[#C59B27] hover:bg-[#B38A1F] py-3.5 text-sm font-semibold text-white shadow-lg transition-all hover:scale-[1.02] active:scale-[0.98]"
                    >
                      Launch Workspace with Topic →
                    </button>
                  </div>
                </form>

                <div className="mt-6 text-center text-[11px] text-slate-400">
                  ✨ Instant access • No credit card required • Guest mode available
                </div>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* =====================================================
          6. "ABOUT THE PLATFORM" (Deep-Dive with Campus Image)
      ====================================================== */}
      <section id="about" className="py-24 px-6 bg-white border-t border-slate-200/60">
        <div className="mx-auto max-w-7xl">
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Column: Mission & Contrasting Value */}
            <div className="lg:col-span-6">
              <span className="text-xs font-bold tracking-widest text-[#C59B27] uppercase">
                Why We Built EduAgent AI
              </span>
              <h2 className="mt-2 text-3xl sm:text-4xl font-serif font-bold text-slate-900 tracking-tight">
                Reinventing Education for the Cognitive Era
              </h2>
              
              <p className="mt-6 text-slate-600 leading-relaxed text-base">
                Traditional online learning suffers from passive reading fatigue: students stare at 100-page slide decks,
                highlight notes without retention, and struggle to discover what they actually misunderstand.
              </p>

              <div className="mt-8 space-y-4">
                <div className="flex items-start gap-3.5">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#C59B27]/10 text-[#C59B27] font-bold text-sm mt-0.5">
                    ✓
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">Decoupled Multi-Agent Specialization</h4>
                    <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">
                      Specialized agents manage vector document ingestion, pedagogical quiz creation, and audio generation independently.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3.5">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#C59B27]/10 text-[#C59B27] font-bold text-sm mt-0.5">
                    ✓
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">Evidence-Based Active Recall & Spaced Repetition</h4>
                    <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">
                      Quizzes and flashcards trigger neurological retrieval practice, multiplying memory retention exponentially.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3.5">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#C59B27]/10 text-[#C59B27] font-bold text-sm mt-0.5">
                    ✓
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">100% Verifiable Vector Grounding</h4>
                    <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">
                      Every response is anchored to your uploaded course materials with source attribution to eliminate hallucinations.
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-10">
                <button
                  onClick={onEnterWorkspace}
                  className="rounded-lg bg-[#0B1220] hover:bg-[#14223D] px-7 py-3.5 text-sm font-semibold text-white shadow-md transition"
                >
                  Enter Agent Workspace →
                </button>
              </div>
            </div>

            {/* Right Column: Campus Image Showcase Container */}
            <div className="lg:col-span-6 relative">
              <div className="rounded-3xl overflow-hidden shadow-2xl border-4 border-white">
                <img
                  src="/images/campus-historic.jpg"
                  alt="Historic University Collegiate Campus"
                  className="w-full h-[420px] object-cover"
                />
              </div>

              {/* Floating Stat Badge */}
              <div className="absolute -bottom-6 -left-6 rounded-2xl bg-white p-5 shadow-xl border border-slate-100 hidden sm:flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#C59B27]/10 text-[#C59B27] text-2xl font-bold">
                  ⚡
                </div>
                <div>
                  <div className="text-lg font-bold text-slate-900">3 Coordinated Agents</div>
                  <div className="text-xs text-slate-500">FastAPI & LangGraph Architecture</div>
                </div>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* =====================================================
          7. "WHOM IS IT FOR?" (Target Audiences)
      ====================================================== */}
      <section id="audience" className="py-24 px-6 bg-slate-50 border-t border-slate-200/60">
        <div className="mx-auto max-w-7xl">
          
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-bold tracking-widest text-[#C59B27] uppercase">
              Designed For Every Learner
            </span>
            <h2 className="mt-2 text-3xl sm:text-4xl font-serif font-bold text-slate-900 tracking-tight">
              Whom Is EduAgent AI Built For?
            </h2>
            <p className="mt-4 text-slate-600 leading-relaxed">
              Whether you are cramming for semester exams, preparing coursework for 100+ students, or mastering a new programming language.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {targetAudiences.map((aud, i) => (
              <div
                key={i}
                className="rounded-2xl bg-white p-7 shadow-[0_10px_25px_-5px_rgba(0,0,0,0.05)] border border-slate-100 transition-all hover:-translate-y-1 hover:shadow-lg flex flex-col justify-between"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 text-2xl mb-4">
                    {aud.icon}
                  </div>
                  <h3 className="text-lg font-serif font-bold text-slate-900 mb-1">
                    {aud.title}
                  </h3>
                  <p className="text-xs font-semibold text-[#C59B27] mb-3">
                    {aud.tagline}
                  </p>
                  <p className="text-xs text-slate-600 leading-relaxed mb-6">
                    {aud.description}
                  </p>
                </div>

                <div className="pt-4 border-t border-slate-100">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Key Features:
                  </div>
                  <ul className="space-y-1.5">
                    {aud.features.map((feat, idx) => (
                      <li key={idx} className="flex items-center gap-1.5 text-xs text-slate-600">
                        <span className="text-[#C59B27]">✦</span>
                        <span>{feat}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* =====================================================
          8. FREQUENTLY ASKED QUESTIONS (FAQ)
      ====================================================== */}
      <section id="faq" className="py-24 px-6 bg-white border-t border-slate-200/60">
        <div className="mx-auto max-w-4xl">
          
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-bold tracking-widest text-[#C59B27] uppercase">
              Have Questions?
            </span>
            <h2 className="mt-2 text-3xl sm:text-4xl font-serif font-bold text-slate-900 tracking-tight">
              Frequently Asked Questions
            </h2>
            <p className="mt-4 text-slate-600 leading-relaxed">
              Everything you need to know about the autonomous educational multi-agent platform.
            </p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, i) => (
              <div
                key={i}
                className="rounded-xl border border-slate-200/80 bg-slate-50/50 overflow-hidden transition-all"
              >
                <button
                  onClick={() => toggleFaq(i)}
                  className="w-full flex items-center justify-between p-5 text-left font-medium text-slate-900 hover:bg-slate-100/60 transition"
                >
                  <span className="text-base font-serif font-semibold pr-4">{faq.q}</span>
                  <span className="text-xl text-[#C59B27] font-bold">
                    {openFaqIndex === i ? "−" : "+"}
                  </span>
                </button>
                {openFaqIndex === i && (
                  <div className="px-5 pb-5 text-sm text-slate-600 leading-relaxed border-t border-slate-200/60 pt-4 bg-white">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* =====================================================
          9. FOOTER (Matching Dark Navy in Reference)
      ====================================================== */}
      <footer className="bg-[#0B1220] border-t border-white/10 text-slate-400 py-14 px-6">
        <div className="mx-auto max-w-7xl flex flex-col md:flex-row items-center justify-between gap-8">
          
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full border-2 border-[#C59B27] bg-[#C59B27]/10 text-[#C59B27] font-serif font-bold text-base">
              SL
            </div>
            <div>
              <div className="text-base font-serif font-bold text-white tracking-wider uppercase">
                SmartLearn
              </div>
              <p className="text-[11px] text-[#D4AF37] font-medium tracking-wider uppercase">
                Autonomous Multi-Agent Educational Platform
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-7 text-xs font-medium text-slate-300">
            <a href="#about" className="hover:text-white transition">About</a>
            <a href="#solutions" className="hover:text-white transition">Solutions</a>
            <a href="#audience" className="hover:text-white transition">Whom to Use</a>
            <a href="#how-it-works" className="hover:text-white transition">How We Work</a>
            <a href="#faq" className="hover:text-white transition">FAQ</a>
            <button onClick={onEnterWorkspace} className="text-[#C59B27] font-bold hover:underline">
              Launch Workspace
            </button>
          </div>

          <div className="text-xs text-slate-400">
            © {new Date().getFullYear()} SmartLearn. All rights reserved.
          </div>

        </div>
      </footer>

    </div>
  );
}
