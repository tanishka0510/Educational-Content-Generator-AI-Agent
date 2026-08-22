"use client";

import { useState } from "react";

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
  onBack: () => void;
}

export default function FlashcardsView({ onBack }: FlashcardsViewProps) {
  // Config state
  const [subject, setSubject] = useState("OS");
  const [difficulty, setDifficulty] = useState("medium");
  const [numCards, setNumCards] = useState(5);
  const [topic, setTopic] = useState("");
  const [documentUploaded, setDocumentUploaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Game state
  const [deck, setDeck] = useState<FlashcardDeck | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [completed, setCompleted] = useState(false);

  const startRevision = async () => {
    setError("");
    setLoading(true);
    setDeck(null);
    setCurrentIndex(0);
    setIsFlipped(false);
    setCompleted(false);

    const token = localStorage.getItem("authToken");
    if (!token) {
      setError("Please log in first.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/flashcards/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          subject,
          topic: topic.trim() || null,
          difficulty,
          number_of_cards: numCards,
          document_uploaded: documentUploaded,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to generate flashcards. Make sure the Content Processing Agent is on 8001.");
      }

      const data = await response.json();
      setDeck(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Error generating flashcards.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (grade: "easy" | "medium" | "hard") => {
    if (!deck) return;

    const currentCard = deck.flashcards[currentIndex];

    // Submit rating to spaced repetition database
    const token = localStorage.getItem("authToken");
    if (token) {
      try {
        await fetch("http://127.0.0.1:8000/flashcards/submit", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            subject: deck.subject,
            topic: deck.topic,
            card_id: `${deck.subject}-${deck.topic || "general"}-${currentCard.id}`,
            grade,
          }),
        });
      } catch (err) {
        console.error("Spaced repetition submit failed:", err);
      }
    }

    // Advance
    if (currentIndex + 1 < deck.flashcards.length) {
      setIsFlipped(false);
      setTimeout(() => {
        setCurrentIndex((prev) => prev + 1);
      }, 300); // Wait for flip transition
    } else {
      setCompleted(true);
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

            {error && (
              <div className="mt-6 rounded-lg bg-rose-950/60 text-rose-400 border border-rose-800 p-4 text-sm">
                {error}
              </div>
            )}

            <div className="mt-8 space-y-5">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Select Subject
                </label>
                <select
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
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
