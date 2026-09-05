"use client";

import { useState, useEffect } from "react";

interface Flashcard {
  id: number;
  front: string;
  back: string;
}

interface FlashcardDeck {
  subject: string;
  topic: string | null;
  difficulty: string;
  flashcards: Flashcard[];
}

interface FlashcardsViewProps {
  initialSubject?: string;
  initialTopic?: string;
  initialDifficulty?: string;
  initialDocumentUploaded?: boolean;
  initialNumCards?: number;
  autoStart?: boolean;
  onSubjectChange?: (subject: string) => void;
  onBack: () => void;
  onAuthFailure?: () => void;
  onRequireAuth?: (message?: string) => void;
}

export default function FlashcardsView({
  initialSubject = "",
  initialTopic = "",
  initialDifficulty = "medium",
  initialDocumentUploaded = false,
  initialNumCards = 5,
  autoStart = false,
  onSubjectChange,
  onBack,
  onAuthFailure,
  onRequireAuth,
}: FlashcardsViewProps) {
  // Config state
  const [subject, setSubject] = useState(initialSubject);
  const [difficulty, setDifficulty] = useState(initialDifficulty);
  const [numCards, setNumCards] = useState(initialNumCards);
  const [topic, setTopic] = useState(initialTopic ?? "");
  const [documentUploaded, setDocumentUploaded] = useState(initialDocumentUploaded);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Sync initialSubject changes from parent
  useEffect(() => {
    if (initialSubject) {
      setSubject(initialSubject);
    }
  }, [initialSubject]);

  useEffect(() => {
    setTopic(initialTopic ?? "");
    setDifficulty(initialDifficulty);
    setNumCards(initialNumCards);
    setDocumentUploaded(initialDocumentUploaded);
  }, [initialTopic, initialDifficulty, initialNumCards, initialDocumentUploaded]);

  const handleSubjectChange = (newSubject: string) => {
    setSubject(newSubject);
    if (onSubjectChange) {
      onSubjectChange(newSubject);
    }
  };

  // Game state
  const [deck, setDeck] = useState<FlashcardDeck | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [completed, setCompleted] = useState(false);

  // Attempt & Review tracking
  const [reviewCounts, setReviewCounts] = useState({ easy: 0, medium: 0, hard: 0 });
  const [deckAttempts, setDeckAttempts] = useState<
    Array<{
      id?: number | string;
      topic?: string;
      difficulty?: string;
      easy_count?: number;
      medium_count?: number;
      hard_count?: number;
      created_at?: string;
    }>
  >([]);
  const [showAttempts, setShowAttempts] = useState(false);

  // Guest usage tracking
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [guestCount, setGuestCount] = useState(0);

  const fetchAttempts = async () => {
    const token = localStorage.getItem("authToken");
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;
    try {
      const res = await fetch(`http://127.0.0.1:8000/flashcards/attempts?subject=${subject}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setDeckAttempts(data);
      }
    } catch (err) {
      console.error("Could not load flashcard attempts:", err);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    setIsLoggedIn(!!token);
    const count = parseInt(localStorage.getItem("guest_flashcard_count") || "0", 10);
    setGuestCount(count);
    fetchAttempts();
  }, [subject]);

  const startRevision = async () => {
    setError("");
    setLoading(true);
    setDeck(null);
    setCurrentIndex(0);
    setIsFlipped(false);
    setCompleted(false);
    setReviewCounts({ easy: 0, medium: 0, hard: 0 });

    const token = localStorage.getItem("authToken");

    // Check free trial limit for unauthenticated guest users
    if (!token) {
      const currentGuestCount = parseInt(localStorage.getItem("guest_flashcard_count") || "0", 10);
      if (currentGuestCount >= 2) {
        setLoading(false);
        if (onRequireAuth) {
          onRequireAuth("You have generated 2 free flashcard sets. Sign in or create an account to unlock unlimited flashcards, quizzes, and chat!");
        } else {
          setError("Free limit reached: You have generated 2 flashcard sets. Please Sign Up or Log In to continue.");
        }
        return;
      }
    }

    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch("http://127.0.0.1:8000/flashcards/generate", {
        method: "POST",
        headers,
        body: JSON.stringify({
          subject,
          topic: topic.trim() || null,
          difficulty,
          number_of_cards: numCards,
          document_uploaded: documentUploaded,
        }),
      });

      if (!response.ok) {
        throw new Error(`Generation failed with code ${response.status}`);
      }

      const data = await response.json();
      setDeck(data);

      // Increment guest flashcard count if unauthenticated
      if (!token) {
        const newCount = (parseInt(localStorage.getItem("guest_flashcard_count") || "0", 10)) + 1;
        localStorage.setItem("guest_flashcard_count", String(newCount));
        setGuestCount(newCount);
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Could not generate flashcards. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (autoStart) startRevision();
  }, [autoStart]);

  const handleReview = async (grade: "easy" | "medium" | "hard") => {
    if (!deck) return;

    const currentCard = deck.flashcards[currentIndex];
    const newCounts = {
      ...reviewCounts,
      [grade]: reviewCounts[grade] + 1,
    };
    setReviewCounts(newCounts);

    // Submit rating to spaced repetition database
    const token = localStorage.getItem("authToken");
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const res = await fetch("http://127.0.0.1:8000/flashcards/submit", {
        method: "POST",
        headers,
        body: JSON.stringify({
          subject: deck.subject,
          topic: deck.topic,
          card_id: `${deck.subject}-${deck.topic || "general"}-${currentCard.id}`,
          grade,
        }),
      });
      if (res.status === 401 && onAuthFailure) {
        onAuthFailure();
        return;
      }
    } catch (err) {
      console.error("Spaced repetition submit failed:", err);
    }

    // Advance or complete deck
    if (currentIndex + 1 < deck.flashcards.length) {
      setIsFlipped(false);
      setTimeout(() => {
        setCurrentIndex((prev) => prev + 1);
      }, 300); // Wait for flip transition
    } else {
      setCompleted(true);
      // Submit full deck attempt session to database
      try {
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (token) headers["Authorization"] = `Bearer ${token}`;

        await fetch("http://127.0.0.1:8000/flashcards/attempt", {
          method: "POST",
          headers,
          body: JSON.stringify({
            subject: deck.subject,
            topic: deck.topic || null,
            difficulty,
            total_cards: deck.flashcards.length,
            cards_reviewed: deck.flashcards.length,
            easy_count: newCounts.easy,
            medium_count: newCounts.medium,
            hard_count: newCounts.hard,
          }),
        });
        fetchAttempts();
      } catch (err) {
        console.error("Failed to save flashcard attempt in DB:", err);
      }
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-16 text-white flex justify-center items-center">
      {/* 3D Flip Styles */}
      <style>{`
        .flashcard-container {
          perspective: 1000px;
        }
        .flashcard-inner {
          position: relative;
          width: 100%;
          height: 100%;
          text-align: center;
          transition: transform 0.6s;
          transform-style: preserve-3d;
        }
        .flashcard-inner.flipped {
          transform: rotateY(180deg);
        }
        .flashcard-front, .flashcard-back {
          position: absolute;
          width: 100%;
          height: 100%;
          backface-visibility: hidden;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          border-radius: 1rem;
          padding: 2rem;
          border: 1px solid #1e293b;
        }
        .flashcard-front {
          background-color: #0f172a;
          color: #f8fafc;
        }
        .flashcard-back {
          background-color: #1e293b;
          color: #cbd5e1;
          transform: rotateY(180deg);
        }
      `}</style>

      <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900/60 p-8 shadow-xl backdrop-blur-md">
        
        {/* Step 1: Config Form */}
        {!deck && !loading && (
          <div>
            <div className="text-center">
              <span className="text-sm font-semibold uppercase tracking-widest text-slate-400">
                AI Flashcards Revision
              </span>
              <h1 className="mt-2 text-3xl font-bold tracking-tight">Active Recall Study</h1>
              <p className="mt-2 text-sm text-slate-400">
                Generate concept cards to master your learning with Spaced Repetition
              </p>
            </div>

            {/* Free Trial Banner for Guests */}
            {!isLoggedIn && (
              <div className="mt-4 flex items-center justify-between rounded-xl border border-sky-800/60 bg-sky-950/40 px-4 py-2.5 text-xs text-sky-300">
                <span>Free Trial: <b>{guestCount} of 2</b> flashcard decks generated</span>
                {onRequireAuth && (
                  <button
                    onClick={() => onRequireAuth("Sign up or log in to unlock unlimited flashcards, quizzes, and chat!")}
                    className="font-medium underline hover:text-white transition"
                  >
                    Sign In for Unlimited →
                  </button>
                )}
              </div>
            )}

            {error && (
              <div className="mt-6 rounded-lg bg-rose-950/60 text-rose-400 border border-rose-800 p-4 text-sm">
                <p>{error}</p>
                {error.includes("limit") && onRequireAuth && (
                  <button
                    onClick={() => onRequireAuth("Sign in or create an account to unlock unlimited flashcards, quizzes, and chat!")}
                    className="mt-3 rounded-lg bg-rose-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-rose-500 transition block"
                  >
                    Sign In / Sign Up Now →
                  </button>
                )}
              </div>
            )}

            {/* Past Deck Attempts Toggle */}
            {deckAttempts.length > 0 && (
              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => setShowAttempts(!showAttempts)}
                  className="flex w-full items-center justify-between rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-2.5 text-xs text-slate-300 transition hover:bg-slate-800 hover:text-white"
                >
                  <span className="flex items-center gap-2 font-medium">
                    <span>🗂️</span>
                    <span>Past Flashcard Sessions for {subject} ({deckAttempts.length})</span>
                  </span>
                  <span>{showAttempts ? "Hide ▲" : "View History ▼"}</span>
                </button>

                {showAttempts && (
                  <div className="mt-2 max-h-48 space-y-1.5 overflow-y-auto rounded-xl border border-slate-800 bg-slate-950/80 p-2.5 text-xs">
                    {deckAttempts.map((att, i) => {
                      const dt = new Date(att.created_at || "").toLocaleDateString(undefined, {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      });
                      return (
                        <div
                          key={att.id || i}
                          className="flex items-center justify-between rounded-lg bg-slate-900/60 px-3 py-2 text-slate-300"
                        >
                          <div>
                            <span className="font-semibold text-white">
                              {att.topic || "General Deck"}
                            </span>
                            <span className="ml-2 text-[10px] uppercase text-slate-500">
                              {att.difficulty}
                            </span>
                            <span className="block text-[10px] text-slate-500">{dt}</span>
                          </div>
                          <div className="flex items-center gap-2 text-[11px]">
                            <span className="text-emerald-400">🟢 {att.easy_count}</span>
                            <span className="text-yellow-400">🟡 {att.medium_count}</span>
                            <span className="text-rose-400">🔴 {att.hard_count}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            <div className="mt-8 space-y-5">

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Select Subject
                </label>
                <select
                  value={subject}
                  onChange={(e) => handleSubjectChange(e.target.value)}
                  className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none focus:border-slate-500"
                >
                  <option value="OS">Operating System</option>
                  <option value="OOP">Object Oriented Programming</option>
                  <option value="DBMS">Database Management System</option>
                  <option value="CNS">Cryptography and Network Security</option>
                  <option value="SE">Software Engineering</option>
                  <option value="AI">Artificial Intelligence</option>
                  <option value="ETC">Effective Technical Communication</option>
                  <option value="COA">Computer Organization and Architecture</option>
                  <option value="DATA STRUCTURE">Data Structure</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Topic (Optional)
                </label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g. Memory segments, TCP handshake"
                  className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none focus:border-slate-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Difficulty
                  </label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Cards Quantity
                  </label>
                  <select
                    value={numCards}
                    onChange={(e) => setNumCards(Number(e.target.value))}
                    className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none"
                  >
                    <option value={3}>3</option>
                    <option value={5}>5</option>
                    <option value={10}>10</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="docModeCards"
                  checked={documentUploaded}
                  onChange={(e) => setDocumentUploaded(e.target.checked)}
                  className="h-4 w-4 rounded border-slate-700 bg-slate-900 text-white focus:ring-0"
                />
                <label htmlFor="docModeCards" className="text-sm text-slate-350 cursor-pointer">
                  Use my uploaded document instead of default textbook database
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={startRevision}
                  className="flex-1 rounded-xl bg-white py-3 text-sm font-semibold text-slate-950 hover:bg-slate-200 transition"
                >
                  Generate Flashcards
                </button>
                <button
                  onClick={onBack}
                  className="rounded-xl border border-slate-700 bg-slate-900 px-5 py-3 text-sm hover:bg-slate-800 transition"
                >
                  Back
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Loading Spinner */}
        {loading && (
          <div className="text-center py-20">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-800 border-t-white mx-auto"></div>
            <p className="mt-4 text-slate-400">Extracting revision cards using AI...</p>
          </div>
        )}

        {/* Step 2: Cards Revision Display */}
        {deck && !completed && (
          <div>
            {/* Header progress */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-lg font-semibold">{deck.subject} Flashcards</h3>
                <span className="text-xs text-slate-400 font-medium">
                  Topic: {deck.topic || "General"}
                </span>
              </div>
              <span className="text-sm font-semibold text-slate-450">
                Card {currentIndex + 1} of {deck.flashcards.length}
              </span>
            </div>

            {/* Flippable Card Container */}
            <div className="mt-8 flashcard-container h-80 w-full">
              <div
                onClick={() => setIsFlipped(!isFlipped)}
                className={`flashcard-inner cursor-pointer ${isFlipped ? "flipped" : ""}`}
              >
                {/* Front Face */}
                <div className="flashcard-front shadow-lg">
                  <span className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-4">
                    FRONT (Recall Concept)
                  </span>
                  <p className="text-xl font-medium text-center leading-relaxed">
                    {deck.flashcards[currentIndex].front}
                  </p>
                  <span className="text-xs text-slate-450 mt-6 animate-pulse">
                    Click card to flip and reveal answer
                  </span>
                </div>

                {/* Back Face */}
                <div className="flashcard-back shadow-lg">
                  <span className="text-xs uppercase tracking-widest text-slate-450 font-bold mb-4">
                    BACK (Answer Details)
                  </span>
                  <p className="text-lg text-center leading-relaxed text-slate-200">
                    {deck.flashcards[currentIndex].back}
                  </p>
                  <span className="text-xs text-slate-500 mt-6">
                    Click card to flip back
                  </span>
                </div>
              </div>
            </div>

            {/* Spaced repetition options: show only when card is flipped */}
            <div className="mt-8 h-20 flex flex-col items-center justify-center">
              {isFlipped ? (
                <div className="w-full">
                  <p className="text-xs text-slate-400 text-center font-medium uppercase tracking-wider mb-3">
                    Rate recall difficulty to update spaced scheduling
                  </p>
                  <div className="grid grid-cols-3 gap-3">
                    <button
                      onClick={() => handleReview("hard")}
                      className="rounded-xl border border-rose-900 bg-rose-950/30 py-2.5 text-sm font-semibold text-rose-400 hover:bg-rose-900/40 transition"
                    >
                      🔴 Hard (1d)
                    </button>
                    <button
                      onClick={() => handleReview("medium")}
                      className="rounded-xl border border-yellow-900 bg-yellow-950/30 py-2.5 text-sm font-semibold text-yellow-400 hover:bg-yellow-900/40 transition"
                    >
                      🟡 Medium (3d+)
                    </button>
                    <button
                      onClick={() => handleReview("easy")}
                      className="rounded-xl border border-emerald-900 bg-emerald-950/30 py-2.5 text-sm font-semibold text-emerald-400 hover:bg-emerald-900/40 transition"
                    >
                      🟢 Easy (7d+)
                    </button>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-500 italic">
                  Flip the card to rate your recall.
                </p>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Finished deck Screen */}
        {completed && (
          <div className="text-center py-8">
            <span className="text-5xl">🎉</span>
            <h2 className="mt-4 text-3xl font-bold">Deck Reviewed!</h2>
            <p className="mt-2 text-sm text-slate-400">
              Spaced repetition logs have been updated.
            </p>
            
            {!isLoggedIn && (
              <div className="mt-6 max-w-md mx-auto rounded-xl border border-sky-800/60 bg-sky-950/40 p-4 text-xs text-sky-200 text-center">
                <p className="font-semibold text-sky-300 text-sm">Want to track your Spaced Repetition learning?</p>
                <p className="mt-1 text-slate-300">Sign in or create an account to remember card intervals, review weak cards, and access your Learning Progress Report.</p>
                {onRequireAuth && (
                  <button
                    onClick={() => onRequireAuth("Sign in or create an account to save your spaced repetition progress and access learning reports.")}
                    className="mt-3 rounded-lg bg-sky-500 px-4 py-2 font-semibold text-white hover:bg-sky-400 transition inline-block"
                  >
                    Sign In / Sign Up to Save Progress →
                  </button>
                )}
              </div>
            )}

            <div className="mt-10 flex gap-4 justify-center">
              <button
                onClick={startRevision}
                className="rounded-xl bg-white px-6 py-2.5 text-sm font-semibold text-slate-950 hover:bg-slate-200 transition"
              >
                Review Again
              </button>
              <button
                onClick={() => setDeck(null)}
                className="rounded-xl border border-slate-700 bg-slate-900 px-6 py-2.5 text-sm font-medium hover:bg-slate-800 transition"
              >
                New Deck
              </button>
              <button
                onClick={onBack}
                className="rounded-xl border border-slate-700 bg-slate-900 px-6 py-2.5 text-sm font-medium hover:bg-slate-800 transition"
              >
                Exit
              </button>
            </div>
          </div>
        )}

      </div>
    </main>
  );
}
