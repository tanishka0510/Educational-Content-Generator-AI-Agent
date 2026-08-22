"use client";

import { useEffect, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line, Doughnut, Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface QuizResult {
  id: number;
  subject: string;
  topic: string | null;
  difficulty: string;
  score: int;
  total_questions: int;
  created_at: string;
}

interface FlashcardProgress {
  id: number;
  subject: string;
  topic: string | null;
  card_id: string;
  next_review_at: string;
}

interface ChatSession {
  id: string;
  subject: string;
  title: string;
  updated_at: string;
}

interface DashboardProps {
  onBack: () => void;
}

export default function Dashboard({ onBack }: DashboardProps) {
  const [quizzes, setQuizzes] = useState<QuizResult[]>([]);
  const [flashcards, setFlashcards] = useState<FlashcardProgress[]>([]);
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("authToken");
      if (!token) {
        setError("User is not authenticated.");
        setLoading(false);
        return;
      }

      const headers = { Authorization: `Bearer ${token}` };
      const baseUrl = "http://127.0.0.1:8000";

      try {
        const [quizRes, cardRes, chatRes] = await Promise.all([
          fetch(`${baseUrl}/quiz/history`, { headers }),
          fetch(`${baseUrl}/flashcards/history`, { headers }),
          fetch(`${baseUrl}/chats`, { headers }),
        ]);

        if (!quizRes.ok || !cardRes.ok || !chatRes.ok) {
          throw new Error("Failed to retrieve dashboard progress metrics.");
        }

        const quizData = await quizRes.json();
        const cardData = await cardRes.json();
        const chatData = await chatRes.json();

        setQuizzes(quizData);
        setFlashcards(cardData);
        setChats(chatData);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("Could not load dashboard data.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const downloadReport = async (format: "pdf" | "csv") => {
    const token = localStorage.getItem("authToken");
    if (!token) return;

    try {
      const response = await fetch(`http://127.0.0.1:8000/reports/${format}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) throw new Error("Report export failed.");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `progress_report_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Error exporting report.");
    }
  };

  // ==========================================================
  // Calculate Aggregations
  // ==========================================================
  const totalQuizzes = quizzes.length;
  const totalChats = chats.length;
  const totalFlashcards = flashcards.length;

  const averageScore =
    totalQuizzes > 0
      ? Math.round(
          (quizzes.reduce((acc, q) => acc + q.score / q.total_questions, 0) /
            totalQuizzes) *
            100
        )
      : 0;

  // Group Quizzes by Subject
  const quizCountsBySubject: Record<string, number> = {};
  quizzes.forEach((q) => {
    quizCountsBySubject[q.subject] = (quizCountsBySubject[q.subject] || 0) + 1;
  });

  // Group Chats by Subject
  const chatCountsBySubject: Record<string, number> = {};
  chats.forEach((c) => {
    chatCountsBySubject[c.subject] = (chatCountsBySubject[c.subject] || 0) + 1;
  });

  // Group Cards by Subject
  const cardCountsBySubject: Record<string, number> = {};
  flashcards.forEach((c) => {
    cardCountsBySubject[c.subject] = (cardCountsBySubject[c.subject] || 0) + 1;
  });

  const subjects = Array.from(
    new Set([
      ...Object.keys(quizCountsBySubject),
      ...Object.keys(chatCountsBySubject),
      ...Object.keys(cardCountsBySubject),
    ])
  );

  // ==========================================================
  // Chart Data Configurations
  // ==========================================================

  // 1. Quiz Score Trend (Line Chart) - Chronological
  const quizTrendData = {
    labels: quizzes
      .slice()
      .reverse()
      .map((q) => new Date(q.created_at).toLocaleDateString()),
    datasets: [
      {
        label: "Quiz Percentage (%)",
        data: quizzes
          .slice()
          .reverse()
          .map((q) => Math.round((q.score / q.total_questions) * 100)),
        borderColor: "#cbd5e1", // slate-300
        backgroundColor: "rgba(203, 213, 225, 0.1)",
        tension: 0.3,
        fill: true,
      },
    ],
  };

  // 2. Quiz Distribution by Subject (Doughnut Chart)
  const doughnutData = {
    labels: subjects,
    datasets: [
      {
        data: subjects.map((sub) => quizCountsBySubject[sub] || 0),
        backgroundColor: [
          "#f43f5e", // rose-500
          "#0ea5e9", // sky-500
          "#10b981", // emerald-500
          "#eab308", // yellow-500
          "#a855f7", // purple-500
          "#f97316", // orange-500
          "#6366f1", // indigo-500
          "#ec4899", // pink-500
          "#14b8a6", // teal-500
        ],
        borderWidth: 1,
      },
    ],
  };

  // 3. Overall Activities by Subject (Bar Chart)
  const barData = {
    labels: subjects,
    datasets: [
      {
        label: "Quizzes Taken",
        data: subjects.map((sub) => quizCountsBySubject[sub] || 0),
        backgroundColor: "rgba(244, 63, 94, 0.7)", // rose-500
      },
      {
        label: "Chats Started",
        data: subjects.map((sub) => chatCountsBySubject[sub] || 0),
        backgroundColor: "rgba(14, 165, 233, 0.7)", // sky-500
      },
      {
        label: "Flashcards Reviewed",
        data: subjects.map((sub) => cardCountsBySubject[sub] || 0),
        backgroundColor: "rgba(16, 185, 129, 0.7)", // emerald-500
      },
    ],
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <p className="text-lg text-slate-400">Loading student analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="text-center">
          <p className="text-lg text-rose-500">{error}</p>
          <button
            onClick={onBack}
            className="mt-6 rounded-lg bg-white px-5 py-2 text-sm text-black"
          >
            Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-white">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between border-b border-slate-800 pb-8">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Learning Dashboard</h1>
            <p className="mt-1 text-slate-400">
              Track your educational scores, revision sessions, and download reports
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => downloadReport("csv")}
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-medium hover:bg-slate-800 transition"
            >
              📊 Export CSV
            </button>
            <button
              onClick={() => downloadReport("pdf")}
              className="rounded-xl bg-white px-4 py-2.5 text-sm font-medium text-slate-950 hover:bg-slate-200 transition"
            >
              📄 Export PDF
            </button>
            <button
              onClick={onBack}
              className="rounded-xl border border-slate-700 bg-slate-900/50 px-4 py-2.5 text-sm font-medium hover:bg-slate-850 transition"
            >
              Back
            </button>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6">
            <p className="text-sm font-medium text-slate-400">Quizzes Taken</p>
            <h3 className="mt-2 text-3xl font-bold">{totalQuizzes}</h3>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6">
            <p className="text-sm font-medium text-slate-400">Average Quiz Score</p>
            <h3 className="mt-2 text-3xl font-bold">{averageScore}%</h3>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6">
            <p className="text-sm font-medium text-slate-400">Conversations Started</p>
            <h3 className="mt-2 text-3xl font-bold">{totalChats}</h3>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6">
            <p className="text-sm font-medium text-slate-400">Cards Reviewed</p>
            <h3 className="mt-2 text-3xl font-bold">{totalFlashcards}</h3>
          </div>
        </div>

        {/* Charts Grid */}
        {totalQuizzes === 0 && totalChats === 0 && totalFlashcards === 0 ? (
          <div className="mt-12 rounded-2xl border border-slate-800 bg-slate-900/30 py-20 text-center">
            <h2 className="text-xl font-medium">No learning activities logged yet</h2>
            <p className="mt-2 text-slate-400">
              Start a chat, take a quiz, or review flashcards to visualize your progress.
            </p>
          </div>
        ) : (
          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            {/* Score Trend (Takes 2 columns if screens are large) */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6 lg:col-span-2">
              <h3 className="text-lg font-semibold mb-4">Quiz Score Trend</h3>
              {quizzes.length > 0 ? (
                <div className="h-72">
                  <Line
                    data={quizTrendData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: { min: 0, max: 100 },
                      },
                    }}
                  />
                </div>
              ) : (
                <div className="flex h-72 items-center justify-center text-slate-500">
                  Take quizzes to view score history.
                </div>
              )}
            </div>

            {/* Doughnut Chart */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
              <h3 className="text-lg font-semibold mb-4">Quizzes Taken by Subject</h3>
              {quizzes.length > 0 ? (
                <div className="h-72 flex items-center justify-center">
                  <Doughnut
                    data={doughnutData}
                    options={{ responsive: true, maintainAspectRatio: false }}
                  />
                </div>
              ) : (
                <div className="flex h-72 items-center justify-center text-slate-500">
                  No quiz distribution details.
                </div>
              )}
            </div>

            {/* Subject Activities Bar Chart */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6 lg:col-span-3">
              <h3 className="text-lg font-semibold mb-4">Subject Engagement Analysis</h3>
              <div className="h-80">
                <Bar
                  data={barData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: { beginAtZero: true },
                    },
                  }}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
