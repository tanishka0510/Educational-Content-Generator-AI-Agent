"use client";

import { useState } from "react";

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

interface QuizViewProps {
  onBack: () => void;
}

export default function QuizView({ onBack }: QuizViewProps) {
  // Setup State
  const [subject, setSubject] = useState("OS");
  const [difficulty, setDifficulty] = useState("medium");
  const [numQuestions, setNumQuestions] = useState(5);
  const [topic, setTopic] = useState("");
  const [documentUploaded, setDocumentUploaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Quiz Game State
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [score, setScore] = useState(0);
  const [completed, setCompleted] = useState(false);

  const startQuiz = async () => {
    setError("");
    setLoading(true);
    setQuizData(null);
    setCurrentQuestionIndex(0);
    setScore(0);
    setCompleted(false);
    setIsAnswered(false);
    setSelectedAnswer(null);

    const token = localStorage.getItem("authToken");
    if (!token) {
      setError("Please log in first.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/quiz/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          subject,
          topic: topic.trim() || null,
          difficulty,
          number_of_questions: numQuestions,
          document_uploaded: documentUploaded,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to generate quiz. Ensure Content Processing agent is running on 8001.");
      }

      const data = await response.json();
      setQuizData(data);
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

  const handleSelectOption = (option: string) => {
    if (isAnswered) return;
    setSelectedAnswer(option);
    setIsAnswered(true);

    const currentQuestion = quizData?.questions[currentQuestionIndex];
    if (option === currentQuestion?.correct_answer) {
      setScore((prev) => prev + 1);
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
      // Submit results to backend database
      const token = localStorage.getItem("authToken");
      if (token) {
        try {
          await fetch("http://127.0.0.1:8000/quiz/submit", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              subject: quizData.subject,
              topic: quizData.topic,
              difficulty: quizData.difficulty,
              score: score + (selectedAnswer === quizData.questions[currentQuestionIndex].correct_answer ? 1 : 0),
              total_questions: quizData.total_questions,
            }),
          });
        } catch (err) {
          console.error("Could not save score in DB:", err);
        }
      }
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-16 text-white flex justify-center items-center">
      <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900/60 p-8 shadow-xl backdrop-blur-md">
        
        {/* Step 1: Config Form */}
        {!quizData && !loading && (
          <div>
            <div className="text-center">
              <span className="text-sm font-semibold uppercase tracking-widest text-slate-400">
                AI Quiz Generator
              </span>
              <h1 className="mt-2 text-3xl font-bold tracking-tight">Test Your Knowledge</h1>
              <p className="mt-2 text-sm text-slate-400">
                Select your subject and difficulty to generate an interactive quiz
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
                  placeholder="e.g. Process scheduling, normal forms"
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
                    Questions Count
                  </label>
                  <select
                    value={numQuestions}
                    onChange={(e) => setNumQuestions(Number(e.target.value))}
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
                  id="docMode"
                  checked={documentUploaded}
                  onChange={(e) => setDocumentUploaded(e.target.checked)}
                  className="h-4 w-4 rounded border-slate-700 bg-slate-900 text-white focus:ring-0"
                />
                <label htmlFor="docMode" className="text-sm text-slate-350 cursor-pointer">
                  Use my uploaded document instead of default textbook database
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={startQuiz}
                  className="flex-1 rounded-xl bg-white py-3 text-sm font-semibold text-slate-950 hover:bg-slate-200 transition"
                >
                  Generate Quiz
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
            <p className="mt-4 text-slate-400">Generating quiz questions with AI...</p>
          </div>
        )}

        {/* Step 2: Active Quiz Game */}
        {quizData && !completed && (
          <div>
            {/* Header progress info */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-lg font-semibold">{quizData.quiz_title}</h3>
                <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
                  {quizData.subject} · {quizData.difficulty}
                </span>
              </div>
              <span className="text-sm font-semibold text-slate-400">
                Question {currentQuestionIndex + 1} of {quizData.total_questions}
              </span>
            </div>

            {/* Question Text */}
            <div className="mt-6">
              <h2 className="text-xl font-medium leading-relaxed">
                {quizData.questions[currentQuestionIndex].question}
              </h2>
            </div>

            {/* Options list */}
            <div className="mt-8 space-y-3">
              {quizData.questions[currentQuestionIndex].options.map((option) => {
                const isCorrect = option === quizData.questions[currentQuestionIndex].correct_answer;
                const isSelected = option === selectedAnswer;
                
                let optionStyle = "border-slate-800 bg-slate-900 hover:border-slate-600 hover:bg-slate-850";
                
                if (isAnswered) {
                  if (isCorrect) {
                    optionStyle = "border-emerald-700 bg-emerald-950/40 text-emerald-400";
                  } else if (isSelected) {
                    optionStyle = "border-rose-700 bg-rose-950/40 text-rose-400";
                  } else {
                    optionStyle = "border-slate-800 bg-slate-900 opacity-60";
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
              <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900/40 p-5">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Explanation
                </p>
                <p className="mt-2 text-sm text-slate-300 leading-relaxed">
                  {quizData.questions[currentQuestionIndex].explanation}
                </p>
              </div>
            )}

            {/* Action buttons */}
            <div className="mt-8 flex justify-end">
              <button
                onClick={handleNext}
                disabled={!isAnswered}
                className="rounded-xl bg-white px-6 py-2.5 text-sm font-semibold text-slate-950 hover:bg-slate-200 transition disabled:opacity-40"
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
            <h2 className="mt-4 text-3xl font-bold">Quiz Completed!</h2>
            <p className="mt-2 text-slate-400">
              You scored {score} out of {quizData.total_questions} questions correct
            </p>
            
            <div className="mt-6 flex justify-center">
              <div className="rounded-full bg-slate-900/80 px-8 py-3 border border-slate-800 font-semibold text-xl">
                Score: {Math.round((score / quizData.total_questions) * 100)}%
              </div>
            </div>

            <div className="mt-10 flex gap-4 justify-center">
              <button
                onClick={startQuiz}
                className="rounded-xl bg-white px-6 py-2.5 text-sm font-semibold text-slate-950 hover:bg-slate-200 transition"
              >
                Retake Quiz
              </button>
              <button
                onClick={() => setQuizData(null)}
                className="rounded-xl border border-slate-700 bg-slate-900 px-6 py-2.5 text-sm font-medium hover:bg-slate-800 transition"
              >
                New Quiz
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
