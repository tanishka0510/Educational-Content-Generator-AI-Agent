"use client";

import { useState, useEffect } from "react";

interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correct_answer: string;
  explanation: string;
}

interface QuizData {
  quiz_title: string;
  subject: string;
  topic: string | null;
  difficulty: string;
  questions: QuizQuestion[];
  total_questions: number;
}

const baseUrl =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface AnswerRecord {
  question: string;
  selected_answer: string;
  correct_answer: string;
  is_correct: boolean;
  topic?: string | null;
}

interface QuizViewProps {
  initialSubject?: string;
  initialTopic?: string;
  initialDifficulty?: string;
  initialDocumentUploaded?: boolean;
  initialNumQuestions?: number;
  autoStart?: boolean;
  onSubjectChange?: (subject: string) => void;
  onBack: () => void;
  onAuthFailure?: () => void;
  onRequireAuth?: (message?: string) => void;
}

export default function QuizView({
  initialSubject = "",
  initialTopic = "",
  initialDifficulty = "medium",
  initialDocumentUploaded = false,
  initialNumQuestions = 5,
  autoStart = false,
  onSubjectChange,
  onBack,
  onAuthFailure,
  onRequireAuth,
}: QuizViewProps) {
  // Setup State
  const [subject, setSubject] = useState(initialSubject);
  const [difficulty, setDifficulty] = useState(initialDifficulty);
  const [numQuestions, setNumQuestions] = useState(initialNumQuestions);
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
    setNumQuestions(initialNumQuestions);
    setDocumentUploaded(initialDocumentUploaded);
  }, [initialTopic, initialDifficulty, initialNumQuestions, initialDocumentUploaded]);

  const handleSubjectChange = (newSubject: string) => {
    setSubject(newSubject);
    if (onSubjectChange) {
      onSubjectChange(newSubject);
    }
  };

  // Quiz Game State
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [score, setScore] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [answersDetail, setAnswersDetail] = useState<AnswerRecord[]>([]);

  // Guest usage state
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [guestCount, setGuestCount] = useState(0);

  const [history, setHistory] = useState<
    Array<{
      id?: number | string;
      score: number;
      total_questions: number;
      topic?: string | null;
      difficulty?: string | null;
      created_at: string;
    }>
  >([]);
  const [showHistory, setShowHistory] = useState(false);

  const fetchHistory = async () => {
    const token = localStorage.getItem("authToken");
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;
    try {
      const res = await fetch(`${baseUrl}/quiz/history?subject=${subject}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (err) {
      console.warn("Could not load quiz history (backend offline):", err);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    setIsLoggedIn(!!token);
    const count = parseInt(localStorage.getItem("guest_quiz_count") || "0", 10);
    setGuestCount(count);
    fetchHistory();
  }, [subject]);


  const startQuiz = async () => {
    setError("");
    const quizSubject = subject.trim();
    if (!quizSubject) {
      setError("Please select a subject before generating a quiz.");
      return;
    }

    const quizTopic = topic.trim();

    setLoading(true);
    setQuizData(null);
    setCurrentQuestionIndex(0);
    setScore(0);
    setCompleted(false);
    setIsAnswered(false);
    setSelectedAnswer(null);
    setAnswersDetail([]);

    const token = localStorage.getItem("authToken");
    
    // Check free trial limit for unauthenticated guest users
    if (!token) {
      const currentGuestCount = parseInt(localStorage.getItem("guest_quiz_count") || "0", 10);
      if (currentGuestCount >= 2) {
        setLoading(false);
        if (onRequireAuth) {
          onRequireAuth("You have generated 2 free quizzes. Sign in or create an account to unlock unlimited quizzes, flashcards, and chat!");
        } else {
          setError("Free limit reached: You have generated 2 quizzes. Please Sign Up or Log In to continue.");
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

      const payload = {
        subject: quizSubject,
        topic: quizTopic || null,
        difficulty,
        number_of_questions: numQuestions,
        document_uploaded: documentUploaded,
      };
      console.debug("Quiz generation payload", payload);

      const response = await fetch(`${baseUrl}/quiz/generate`, {
        method: "POST",
        headers,
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        if (response.status === 401 && onAuthFailure) {
          onAuthFailure();
          return;
        }
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to generate quiz. Ensure Content Processing agent is running on 8001.");
      }

      const data = await response.json();
      setQuizData(data);

      // Increment guest quiz count if unauthenticated
      if (!token) {
        const newCount = (parseInt(localStorage.getItem("guest_quiz_count") || "0", 10)) + 1;
        localStorage.setItem("guest_quiz_count", String(newCount));
        setGuestCount(newCount);
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Error generating quiz.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (autoStart) startQuiz();
  }, [autoStart]);

  const handleSelectOption = (option: string) => {
    if (isAnswered) return;
    setSelectedAnswer(option);
    setIsAnswered(true);

    const currentQuestion = quizData?.questions[currentQuestionIndex];
    const isCorrect = option === currentQuestion?.correct_answer;
    if (isCorrect) {
      setScore((prev) => prev + 1);
    }

    if (currentQuestion) {
      setAnswersDetail((prev) => [
        ...prev,
        {
          question: currentQuestion.question,
          selected_answer: option,
          correct_answer: currentQuestion.correct_answer,
          is_correct: isCorrect,
          topic: quizData?.topic || null,
        }
      ]);
    }
  };

  const handleNext = async () => {
    if (!quizData) return;

    if (currentQuestionIndex + 1 < quizData.total_questions) {
      setCurrentQuestionIndex((prev) => prev + 1);
      setSelectedAnswer(null);
      setIsAnswered(false);
    } else {
      setCompleted(true);
      
      // Submit results and question details to backend database (saved for both registered & guest users)
      const token = localStorage.getItem("authToken");
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      try {
        const finalScore = score + (selectedAnswer === quizData.questions[currentQuestionIndex].correct_answer ? 1 : 0);
        await fetch(`${baseUrl}/quiz/submit`, {
          method: "POST",
          headers,
          body: JSON.stringify({
            subject: quizData.subject,
            topic: quizData.topic,
            difficulty: quizData.difficulty,
            score: finalScore,
            total_questions: quizData.total_questions,
            answers_detail: answersDetail,
          }),
        });
      } catch (err) {
        console.error("Could not save score in DB:", err);
      }
    }
  };


  return (
    <main className="min-h-screen bg-[#F8FAFC] px-4 py-16 text-slate-900 flex justify-center items-center font-sans">
      <div className="w-full max-w-2xl rounded-2xl border border-slate-200/80 bg-white p-8 shadow-xl">
        
        {/* Step 1: Config Form */}
        {!quizData && !loading && (
          <div>
            <div className="text-center">
              <span className="inline-block rounded-full border border-[#C59B27]/40 bg-amber-50 px-3 py-1 text-xs font-semibold uppercase tracking-widest text-[#C59B27]">
                AI Examination Suite
              </span>
              <h1 className="mt-3 font-serif text-3xl font-medium tracking-tight text-slate-900">Test Your Knowledge</h1>
              <p className="mt-2 text-sm text-slate-600">
                Generate an adaptive, curriculum-aligned interactive quiz
              </p>
            </div>

            {/* Free Trial Banner for Guests */}
            {!isLoggedIn && (
              <div className="mt-4 flex items-center justify-between rounded-xl border border-[#C59B27]/30 bg-amber-50/80 px-4 py-2.5 text-xs text-[#9A7318]">
                <span>Free Trial: <b>{guestCount} of 2</b> quizzes generated</span>
                {onRequireAuth && (
                  <button
                    onClick={() => onRequireAuth("Sign up or log in to unlock unlimited quizzes, flashcards, and chat!")}
                    className="font-semibold text-[#C59B27] underline hover:text-slate-900 transition"
                  >
                    Sign In for Unlimited →
                  </button>
                )}
              </div>
            )}

            {error && (
              <div className="mt-6 rounded-lg bg-rose-50 text-rose-600 border border-rose-200 p-4 text-sm">
                <p>{error}</p>
                {error.includes("limit") && onRequireAuth && (
                  <button
                    onClick={() => onRequireAuth("Sign in or create an account to unlock unlimited quizzes, flashcards, and chat!")}
                    className="mt-3 rounded-lg bg-rose-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-rose-500 transition block shadow-sm"
                  >
                    Sign In / Sign Up Now →
                  </button>
                )}
              </div>
            )}

            {/* Past Attempts Toggle */}
            {history.length > 0 && (
              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => setShowHistory(!showHistory)}
                  className="flex w-full items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-xs text-slate-700 transition hover:border-[#C59B27]/40 hover:bg-slate-100 hover:text-slate-900"
                >
                  <span className="flex items-center gap-2 font-medium">
                    <span>📜</span>
                    <span>Past Quiz Attempts for {subject} ({history.length})</span>
                  </span>
                  <span>{showHistory ? "Hide ▲" : "View History ▼"}</span>
                </button>

                {showHistory && (
                  <div className="mt-2 max-h-48 space-y-1.5 overflow-y-auto rounded-xl border border-slate-200 bg-slate-50/70 p-2.5 text-xs">
                    {history.map((h, i) => {
                      const pct = Math.round((h.score / h.total_questions) * 100);
                      const dt = new Date(h.created_at).toLocaleDateString(undefined, {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      });
                      return (
                        <div
                          key={h.id || i}
                          className="flex items-center justify-between rounded-lg bg-white border border-slate-100 px-3 py-2 text-slate-700 shadow-2xs"
                        >
                          <div>
                            <span className="font-semibold text-slate-900">
                              {h.topic || "General"}
                            </span>
                            <span className="ml-2 text-[10px] uppercase text-slate-500">
                              {h.difficulty}
                            </span>
                            <span className="block text-[10px] text-slate-400">{dt}</span>
                          </div>
                          <div className="text-right">
                            <span
                              className={`font-bold ${
                                pct >= 80
                                  ? "text-emerald-600"
                                  : pct >= 50
                                  ? "text-amber-600"
                                  : "text-rose-600"
                              }`}
                            >
                              {h.score} / {h.total_questions} ({pct}%)
                            </span>
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
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Select Subject <span className="text-[#C59B27]">*</span>
                </label>
                <select
                  value={subject}
                  onChange={(e) => handleSubjectChange(e.target.value)}
                  className="mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#C59B27] focus:bg-white focus:ring-1 focus:ring-[#C59B27]/30 transition"
                >
                  <option value="">-- Select Subject --</option>
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
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Topic (Optional)
                </label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g. Process scheduling, normal forms"
                  className="mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#C59B27] focus:bg-white focus:ring-1 focus:ring-[#C59B27]/30 transition"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Difficulty
                  </label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#C59B27] focus:bg-white"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Questions Count
                  </label>
                  <select
                    value={numQuestions}
                    onChange={(e) => setNumQuestions(Number(e.target.value))}
                    className="mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none focus:border-[#C59B27] focus:bg-white"
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
                  id="docMode"
                  checked={documentUploaded}
                  onChange={(e) => setDocumentUploaded(e.target.checked)}
                  className="h-4 w-4 rounded border-slate-300 bg-slate-50 text-[#C59B27] accent-[#C59B27] focus:ring-0"
                />
                <label htmlFor="docMode" className="text-sm text-slate-600 cursor-pointer">
                  Use my uploaded document instead of default textbook database
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={startQuiz}
                  className="flex-1 rounded-xl bg-[#C59B27] py-3 text-sm font-bold text-white hover:bg-[#B38A1F] transition shadow-md"
                >
                  Generate Quiz
                </button>
                <button
                  onClick={onBack}
                  className="rounded-xl border border-slate-200 bg-slate-100 px-5 py-3 text-sm font-medium text-slate-700 hover:border-[#C59B27]/40 hover:bg-slate-200 hover:text-slate-900 transition"
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
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-[#C59B27] mx-auto"></div>
            <p className="mt-4 text-slate-600 font-medium">Synthesizing quiz questions with AI...</p>
          </div>
        )}

        {/* Step 2: Active Quiz Game */}
        {quizData && !completed && (
          <div>
            {/* Header progress info */}
            <div className="flex items-center justify-between border-b border-slate-200 pb-4">
              <div>
                <h3 className="font-serif text-xl font-semibold text-slate-900">{quizData.quiz_title}</h3>
                <span className="mt-1 inline-block rounded-full border border-[#C59B27]/40 bg-amber-50 px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider text-[#C59B27]">
                  {quizData.subject} · {quizData.difficulty}
                </span>
              </div>
              <span className="text-sm font-semibold text-slate-500">
                Question {currentQuestionIndex + 1} of {quizData.total_questions}
              </span>
            </div>

            {/* Question Text */}
            <div className="mt-6">
              <h2 className="font-serif text-2xl font-normal leading-relaxed text-slate-900">
                {quizData.questions[currentQuestionIndex].question}
              </h2>
            </div>

            {/* Options list */}
            <div className="mt-8 space-y-3">
              {quizData.questions[currentQuestionIndex].options.map((option) => {
                const isCorrect = option === quizData.questions[currentQuestionIndex].correct_answer;
                const isSelected = option === selectedAnswer;
                
                let optionStyle = "border-slate-200 bg-slate-50/70 hover:border-[#C59B27] hover:bg-amber-50/30 text-slate-800";
                
                if (isAnswered) {
                  if (isCorrect) {
                    optionStyle = "border-emerald-500 bg-emerald-50 text-emerald-800 font-semibold";
                  } else if (isSelected) {
                    optionStyle = "border-rose-500 bg-rose-50 text-rose-800 font-semibold";
                  } else {
                    optionStyle = "border-slate-100 bg-slate-50/40 text-slate-400 opacity-60";
                  }
                }

                return (
                  <button
                    key={option}
                    disabled={isAnswered}
                    onClick={() => handleSelectOption(option)}
                    className={`w-full text-left rounded-xl border p-4 text-sm font-medium transition ${optionStyle}`}
                  >
                    {option}
                  </button>
                );
              })}
            </div>

            {/* Explanation box */}
            {isAnswered && (
              <div className="mt-6 rounded-xl border border-[#C59B27]/30 bg-amber-50/70 p-5">
                <p className="text-xs font-semibold uppercase tracking-wider text-[#C59B27]">
                  Academic Explanation
                </p>
                <p className="mt-2 text-sm text-slate-700 leading-relaxed">
                  {quizData.questions[currentQuestionIndex].explanation}
                </p>
              </div>
            )}

            {/* Action buttons */}
            <div className="mt-8 flex justify-end">
              <button
                onClick={handleNext}
                disabled={!isAnswered}
                className="rounded-xl bg-[#C59B27] px-6 py-2.5 text-sm font-bold text-white hover:bg-[#B38A1F] transition disabled:opacity-40 shadow-md"
              >
                {currentQuestionIndex + 1 === quizData.total_questions ? "Finish Quiz" : "Next Question"}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Finished Score Screen */}
        {completed && quizData && (
          <div className="text-center py-8">
            <span className="text-5xl">🏆</span>
            <h2 className="mt-4 font-serif text-3xl font-medium text-slate-900">Quiz Completed!</h2>
            <p className="mt-2 text-slate-600">
              You scored {score} out of {quizData.total_questions} questions correct
            </p>
            
            <div className="mt-6 flex justify-center">
              <div className="rounded-full bg-amber-50 px-8 py-3 border border-[#C59B27]/40 font-serif font-bold text-xl text-[#C59B27] shadow-sm">
                Score: {Math.round((score / quizData.total_questions) * 100)}%
              </div>
            </div>

            {!isLoggedIn && (
              <div className="mt-6 max-w-md mx-auto rounded-xl border border-[#C59B27]/30 bg-amber-50/60 p-4 text-xs text-slate-700 text-center">
                <p className="font-semibold text-[#C59B27] text-sm">Want to save your scores & track learning progress?</p>
                <p className="mt-1 text-slate-600">Create a free account to unlock unlimited quizzes, flashcards, and personalized progress reports with concept remediation analytics.</p>
                {onRequireAuth && (
                  <button
                    onClick={() => onRequireAuth("Sign in or create an account to save your scores and access complete learning reports.")}
                    className="mt-3 rounded-lg bg-[#C59B27] px-4 py-2 font-bold text-white hover:bg-[#B38A1F] transition inline-block shadow-md"
                  >
                    Sign In / Sign Up to Save Progress →
                  </button>
                )}
              </div>
            )}

            <div className="mt-10 flex gap-4 justify-center">
              <button
                onClick={startQuiz}
                className="rounded-xl bg-[#C59B27] px-6 py-2.5 text-sm font-bold text-white hover:bg-[#B38A1F] transition shadow-md"
              >
                Retake Quiz
              </button>
              <button
                onClick={() => setQuizData(null)}
                className="rounded-xl border border-slate-200 bg-slate-100 px-6 py-2.5 text-sm font-medium text-slate-700 hover:border-[#C59B27]/40 hover:bg-slate-200 transition"
              >
                New Quiz
              </button>
              <button
                onClick={onBack}
                className="rounded-xl border border-slate-200 bg-slate-100 px-6 py-2.5 text-sm font-medium text-slate-700 hover:border-[#C59B27]/40 hover:bg-slate-200 transition"
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
