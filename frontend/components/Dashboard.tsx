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
import StudyPlanModal, { StudyPlanData } from "./StudyPlanModal";


const baseUrl =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

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
  score: number;
  total_questions: number;
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

interface UploadedDoc {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  subject: string;
  topic?: string;
  chunks_count: number;
  status: string;
  created_at: string;
}

interface FlashcardAttemptRecord {
  id: number;
  subject: string;
  topic?: string;
  difficulty: string;
  total_cards: number;
  cards_reviewed: number;
  easy_count: number;
  medium_count: number;
  hard_count: number;
  created_at: string;
}

interface RemediatedQuestion {
  question: string;
  subject: string;
  topic: string;
  initial_date: string;
  remediated_date: string;
  explanation: string;
}

interface SubjectProgress {
  initial_score: number;
  latest_score: number;
  delta: number;
  remediated_count: number;
  description: string;
  quizzes_taken: number;
}

interface Achievement {
  name: string;
  unlocked: boolean;
  description: string;
}

interface AnalyticsReport {
  user_name: string;
  student_email: string;
  report_date: string;
  overall_progress_status: string;
  status_narrative: string;
  total_quizzes: number;
  total_questions_attempted: number;
  total_questions_correct: number;
  average_score: number;
  comparison: {
    baseline_avg: number;
    recent_avg: number;
    growth_delta: number;
    trend: string;
  };
  subject_learning_progress: Record<string, SubjectProgress>;
  remediated_questions: RemediatedQuestion[];
  strengths: string[];
  areas_for_improvement: string[];
  learning_goals: string[];
  achievements: Achievement[];
}

interface DashboardProps {
  onBack: () => void;
  onAuthFailure?: () => void;
}

const SUBJECT_NAMES: Record<string, string> = {
  OS: "Operating System",
  OOP: "Object Oriented Programming",
  DBMS: "Database Management System",
  CNS: "Cryptography and Network Security",
  SE: "Software Engineering",
  AI: "Artificial Intelligence",
  ETC: "Effective Technical Communication",
  COA: "Computer Organization and Architecture",
  "DATA STRUCTURE": "Data Structure",
};

export default function Dashboard({ onBack, onAuthFailure }: DashboardProps) {
  const [quizzes, setQuizzes] = useState<QuizResult[]>([]);
  const [flashcards, setFlashcards] = useState<FlashcardProgress[]>([]);
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [documents, setDocuments] = useState<UploadedDoc[]>([]);
  const [deckAttempts, setDeckAttempts] = useState<FlashcardAttemptRecord[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Study Plan State
  const [isStudyPlanOpen, setIsStudyPlanOpen] = useState(false);
  const [studyPlanData, setStudyPlanData] = useState<StudyPlanData | null>(null);
  const [isStudyPlanLoading, setIsStudyPlanLoading] = useState(false);
  const [isDownloadingStudyPlanPdf, setIsDownloadingStudyPlanPdf] = useState(false);

  const handleDeleteDoc = async (docId: number) => {
    const token = localStorage.getItem("authToken");
    if (!confirm("Are you sure you want to delete this document from your repository?")) return;
    try {
      const res = await fetch(`${baseUrl}/upload/documents/${docId}`, {
        method: "DELETE",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        setDocuments((prev) => prev.filter((d) => d.id !== docId));
      }
    } catch (err) {
      console.error("Failed to delete document:", err);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("authToken");
      if (!token) {
        setError("User is not authenticated.");
        setLoading(false);
        return;
      }

      const headers = { Authorization: `Bearer ${token}` };
      const baseUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

      try {
        const [quizRes, cardRes, chatRes, docRes, attemptRes, analyticsRes] = await Promise.all([
          fetch(`${baseUrl}/quiz/history`, { headers }),
          fetch(`${baseUrl}/flashcards/history`, { headers }),
          fetch(`${baseUrl}/chats`, { headers }),
          fetch(`${baseUrl}/upload/documents`, { headers }),
          fetch(`${baseUrl}/flashcards/attempts`, { headers }),
          fetch(`${baseUrl}/reports/analytics`, { headers }),
        ]);

        if (
          quizRes.status === 401 ||
          cardRes.status === 401 ||
          chatRes.status === 401 ||
          analyticsRes.status === 401
        ) {
          if (onAuthFailure) {
            onAuthFailure();
            return;
          }
        }

        if (!quizRes.ok || !cardRes.ok || !chatRes.ok) {
          throw new Error("Failed to retrieve dashboard progress metrics.");
        }

        const quizData = await quizRes.json();
        const cardData = await cardRes.json();
        const chatData = await chatRes.json();
        const docData = docRes.ok ? await docRes.json() : [];
        const attemptData = attemptRes.ok ? await attemptRes.json() : [];
        const analyticsData = analyticsRes.ok ? await analyticsRes.json() : null;

        setQuizzes(quizData);
        setFlashcards(cardData);
        setChats(chatData);
        setDocuments(docData);
        setDeckAttempts(attemptData);
        setAnalytics(analyticsData);
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
  }, [onAuthFailure]);


  const downloadReport = async (format: "pdf" | "csv") => {
    const token = localStorage.getItem("authToken");
    if (!token) return;

    try {
      const response = await fetch(`${baseUrl}/reports/${format}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        if (response.status === 401 && onAuthFailure) {
          onAuthFailure();
          return;
        }
        throw new Error("Report export failed.");
      }

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

  const openStudyPlan = async () => {
    setIsStudyPlanOpen(true);
    if (!studyPlanData) {
      setIsStudyPlanLoading(true);
      const token = localStorage.getItem("authToken");
      try {
        const response = await fetch(`${baseUrl}/reports/study-plan`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (response.ok) {
          const data = await response.json();
          setStudyPlanData(data);
        } else {
          console.error("Failed to load study plan JSON");
        }
      } catch (err) {
        console.error("Error fetching study plan:", err);
      } finally {
        setIsStudyPlanLoading(false);
      }
    }
  };

  const downloadStudyPlanPdf = async () => {
    const token = localStorage.getItem("authToken");
    setIsDownloadingStudyPlanPdf(true);
    try {
      const response = await fetch(`${baseUrl}/reports/study-plan/pdf`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!response.ok) {
        if (response.status === 401 && onAuthFailure) {
          onAuthFailure();
          return;
        }
        throw new Error("Study plan PDF export failed.");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `weekly_study_plan_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Error exporting study plan PDF.");
    } finally {
      setIsDownloadingStudyPlanPdf(false);
    }
  };

  // ==========================================================
  // Calculate Aggregations
  // ==========================================================
  const totalQuizzes = quizzes.length;

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
        borderColor: "#38bdf8", // sky-400
        backgroundColor: "rgba(56, 189, 248, 0.15)",
        tension: 0.3,
        fill: true,
      },
    ],
  };

  // 2. Quiz Distribution by Subject (Doughnut Chart)
  const doughnutData = {
    labels: subjects.map((s) => SUBJECT_NAMES[s] || s),
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
    labels: subjects.map((s) => SUBJECT_NAMES[s] || s),
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
      <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC] text-slate-800 font-sans">
        <p className="text-lg text-slate-500 font-medium">Loading student analytics & progress reports...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#F8FAFC] text-slate-800 font-sans">
        <div className="text-center">
          <p className="text-lg text-rose-600 font-medium">{error}</p>
          <button
            onClick={onBack}
            className="mt-6 rounded-lg bg-[#C59B27] px-5 py-2 text-sm font-semibold text-white shadow-sm"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-[#F8FAFC] px-6 py-12 text-slate-900 font-sans">
      <div className="mx-auto max-w-6xl">
        
        {/* Top Header */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between border-b border-slate-200 pb-8">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="font-serif text-4xl font-normal tracking-tight text-slate-900">Academic Performance Dashboard</h1>
              {analytics?.overall_progress_status && (
                <span className="rounded-full border border-[#C59B27]/40 bg-amber-50 px-3.5 py-1 text-xs font-semibold text-[#C59B27]">
                  {analytics.overall_progress_status}
                </span>
              )}
            </div>
            <p className="mt-2 text-sm text-slate-600">
              Logged in as <span className="text-[#C59B27] font-semibold">{analytics?.user_name}</span> ({analytics?.student_email})
              {analytics?.report_date && ` • Report Generated: ${analytics.report_date}`}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={openStudyPlan}
              className="flex items-center gap-2 rounded-xl bg-[#C59B27] px-4 py-2.5 text-sm font-bold text-white shadow-md hover:bg-[#B38A1F] transition"
            >
              <span>📅</span>
              <span>Weekly Study Plan</span>
            </button>
            <button
              onClick={() => downloadReport("csv")}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:border-[#C59B27]/40 hover:bg-slate-50 transition shadow-2xs"
            >
              📊 Export CSV
            </button>
            <button
              onClick={() => downloadReport("pdf")}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:border-[#C59B27]/40 hover:bg-slate-50 transition shadow-2xs"
            >
              📄 Export PDF
            </button>
            <button
              onClick={onBack}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:border-[#C59B27]/40 hover:bg-slate-50 transition shadow-2xs"
            >
              ← Back
            </button>
          </div>
        </div>

        {/* ==========================================================
            Section: Personalized Weekly Study Plan Banner
        ========================================================== */}
        <div className="mt-8 rounded-2xl border border-[#C59B27]/30 bg-gradient-to-r from-amber-50/90 via-white to-amber-50/70 p-6 shadow-md relative overflow-hidden">
          <div className="absolute right-0 top-0 translate-x-10 -translate-y-10 w-60 h-60 bg-[#C59B27]/10 rounded-full blur-3xl pointer-events-none"></div>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6 relative z-10">
            <div className="space-y-2">
              <div className="flex items-center gap-2.5">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100 border border-[#C59B27]/40 text-lg text-[#C59B27]">
                  📅
                </span>
                <span className="rounded-full border border-[#C59B27]/40 bg-amber-50 px-3 py-0.5 text-xs font-bold text-[#C59B27]">
                  AI Academic Coach
                </span>
              </div>
              <h2 className="font-serif text-2xl font-medium text-slate-900">
                Personalized Weekly Study Plan & Remediation Schedule
              </h2>
              <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
                A custom 7-day learning routine tailored to your recent quiz errors, difficult flashcards, and knowledge gaps. Includes subject-wise topic diagnosis and actionable improvement strategies.
              </p>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              <button
                onClick={openStudyPlan}
                className="flex items-center gap-2 rounded-xl bg-[#C59B27] px-5 py-3 text-sm font-bold text-white shadow-md hover:bg-[#B38A1F] transition"
              >
                <span>🔍</span>
                <span>View Study Plan</span>
              </button>
              <button
                onClick={downloadStudyPlanPdf}
                disabled={isDownloadingStudyPlanPdf}
                className="flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-700 hover:border-[#C59B27]/40 hover:bg-slate-50 transition shadow-2xs"
              >
                <span>📄</span>
                <span>{isDownloadingStudyPlanPdf ? "Exporting..." : "Download Plan (PDF)"}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm hover:border-[#C59B27]/40 transition">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Quizzes Taken</p>
            <h3 className="mt-2 font-serif text-3xl font-bold text-slate-900">{totalQuizzes}</h3>
            <p className="mt-1 text-xs text-slate-400">{analytics?.total_questions_attempted || 0} questions answered</p>
          </div>

          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm hover:border-[#C59B27]/40 transition">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Average Quiz Score</p>
            <h3 className="mt-2 font-serif text-3xl font-bold text-[#C59B27]">{averageScore}%</h3>
            <p className="mt-1 text-xs text-slate-400">{analytics?.total_questions_correct || 0} correct answers</p>
          </div>

          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm hover:border-[#C59B27]/40 transition">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Score Progression Growth</p>
            <h3 className="mt-2 font-serif text-3xl font-bold text-emerald-600">
              {analytics?.comparison ? `${analytics.comparison.growth_delta > 0 ? "+" : ""}${analytics.comparison.growth_delta}%` : "0%"}
            </h3>
            <p className="mt-1 text-xs text-slate-400">
              Baseline {analytics?.comparison?.baseline_avg || 0}% → Recent {analytics?.comparison?.recent_avg || 0}%
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm hover:border-[#C59B27]/40 transition">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Concepts Remediated</p>
            <h3 className="mt-2 font-serif text-3xl font-bold text-[#C59B27]">
              {analytics?.remediated_questions?.length || 0}
            </h3>
            <p className="mt-1 text-xs text-slate-400">Mistakes turned into correct answers</p>
          </div>
        </div>

        {/* Narrative Banner */}
        {analytics?.status_narrative && (
          <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-700 shadow-2xs">
            <span className="font-semibold text-slate-900 mr-2">Overall Progress Status:</span>
            {analytics.status_narrative}
          </div>
        )}

        {/* ==========================================================
            Section: Learning Progress (Comparing Answers Over Time)
        ========================================================== */}
        <div className="mt-12">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="font-serif text-2xl font-normal tracking-tight text-slate-900">Learning Progress by Subject</h2>
              <p className="text-sm text-slate-600">
                Measures progress in each subject by comparing student test attempts and answer changes over time
              </p>
            </div>
          </div>

          {analytics?.subject_learning_progress && Object.keys(analytics.subject_learning_progress).some(k => analytics.subject_learning_progress[k].quizzes_taken > 0) ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {Object.entries(analytics.subject_learning_progress)
                .filter(([, prog]) => prog.quizzes_taken > 0)
                .map(([subKey, prog]) => (
                  <div key={subKey} className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm hover:border-[#C59B27]/40 transition">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-slate-900">{SUBJECT_NAMES[subKey] || subKey}</h3>
                      <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${prog.delta > 0 ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : prog.delta === 0 ? "bg-slate-100 text-slate-600" : "bg-rose-50 text-rose-700 border border-rose-200"}`}>
                        {prog.delta > 0 ? `+${prog.delta}%` : `${prog.delta}%`}
                      </span>
                    </div>

                    <div className="mt-4 flex items-center justify-between text-xs text-slate-500 border-b border-slate-100 pb-3">
                      <div>
                        <span>Initial Score: </span>
                        <b className="text-[#C59B27]">{prog.initial_score}%</b>
                      </div>
                      <div>
                        <span>Latest Score: </span>
                        <b className="text-[#C59B27]">{prog.latest_score}%</b>
                      </div>
                      <div>
                        <span>Remediated: </span>
                        <b className="text-emerald-600">{prog.remediated_count}</b>
                      </div>
                    </div>

                    <p className="mt-3 text-xs leading-5 text-slate-600">
                      {prog.description}
                    </p>
                  </div>
                ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-500 text-sm shadow-2xs">
              Complete multiple quizzes in your subjects to generate answer comparison and learning progress curves.
            </div>
          )}

          {/* Remediated Question Log */}
          {analytics?.remediated_questions && analytics.remediated_questions.length > 0 && (
            <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50/50 p-5 shadow-2xs">
              <h3 className="font-semibold text-emerald-800 text-sm mb-3">
                🎯 Concepts Successfully Remediated (Initial Error → Subsequent Correct Answer):
              </h3>
              <div className="space-y-2">
                {analytics.remediated_questions.map((rq, idx) => (
                  <div key={idx} className="rounded-xl border border-slate-200 bg-white p-3 text-xs text-slate-700 shadow-2xs">
                    <p className="font-medium text-slate-900">
                      [{SUBJECT_NAMES[rq.subject] || rq.subject}] {rq.question}
                    </p>
                    <p className="mt-1 text-slate-600">
                      Initially answered incorrectly on <span className="text-rose-600">{rq.initial_date}</span>, then mastered and answered correctly on <span className="text-emerald-700 font-medium">{rq.remediated_date}</span>.
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ==========================================================
            Section: Charts Grid
        ========================================================== */}
        {totalQuizzes > 0 && (
          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            {/* Score Trend */}
            <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm lg:col-span-2">
              <h3 className="font-serif text-lg font-normal text-slate-900 mb-4">Quiz Score Progression Trend</h3>
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
            </div>

            {/* Doughnut Chart */}
            <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm">
              <h3 className="font-serif text-lg font-normal text-slate-900 mb-4">Quizzes by Subject</h3>
              <div className="h-72 flex items-center justify-center">
                <Doughnut
                  data={doughnutData}
                  options={{ responsive: true, maintainAspectRatio: false }}
                />
              </div>
            </div>

            {/* Subject Activities Bar Chart */}
            <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm lg:col-span-3">
              <h3 className="font-serif text-lg font-normal text-slate-900 mb-4">Subject Engagement Breakdown</h3>
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

        {/* ==========================================================
            Section: Uploaded Study Documents & Flashcard Sessions
        ========================================================== */}
        <div className="mt-12 grid gap-6 lg:grid-cols-2">
          {/* Uploaded Documents Repository */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <h3 className="font-serif text-lg font-normal text-slate-900 flex items-center gap-2">
                <span>📁</span> Uploaded Study Materials ({documents.length})
              </h3>
              <span className="text-xs text-[#C59B27] font-semibold">Stored in Database</span>
            </div>

            {documents.length === 0 ? (
              <div className="mt-6 rounded-xl border border-dashed border-slate-300 p-8 text-center text-xs text-slate-400">
                <span className="text-2xl block mb-2">📄</span>
                No documents uploaded yet. Upload lecture notes or textbooks in Chat to see them saved here!
              </div>
            ) : (
              <div className="mt-4 max-h-72 space-y-2.5 overflow-y-auto pr-1">
                {documents.map((doc) => {
                  const sizeKb = Math.round(doc.file_size / 1024);
                  const uploadDate = new Date(doc.created_at).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                  });
                  return (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 p-3 text-xs transition hover:border-[#C59B27]/40"
                    >
                      <div className="min-w-0 flex-1 pr-3">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-900 truncate">{doc.filename}</span>
                          <span className="rounded border border-[#C59B27]/40 bg-amber-50 px-1.5 py-0.5 text-[10px] font-bold text-[#C59B27]">
                            {doc.subject}
                          </span>
                        </div>
                        <div className="mt-1 flex items-center gap-2 text-[11px] text-slate-500">
                          <span>{sizeKb > 0 ? `${sizeKb} KB` : "Document"}</span>
                          <span>•</span>
                          <span>{doc.chunks_count} chunks indexed</span>
                          <span>•</span>
                          <span>{uploadDate}</span>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleDeleteDoc(doc.id)}
                        title="Delete document"
                        className="rounded p-1 text-slate-400 transition hover:bg-rose-50 hover:text-rose-600"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Flashcard Revision Sessions Log */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <h3 className="font-serif text-lg font-normal text-slate-900 flex items-center gap-2">
                <span>🗂️</span> Flashcard Study Sessions ({deckAttempts.length})
              </h3>
              <span className="text-xs text-[#C59B27] font-semibold">Attempt History</span>
            </div>

            {deckAttempts.length === 0 ? (
              <div className="mt-6 rounded-xl border border-dashed border-slate-300 p-8 text-center text-xs text-slate-400">
                <span className="text-2xl block mb-2">🃏</span>
                No flashcard revision sessions logged yet. Complete a flashcard deck to track your reviews!
              </div>
            ) : (
              <div className="mt-4 max-h-72 space-y-2.5 overflow-y-auto pr-1">
                {deckAttempts.map((att, idx) => {
                  const dateStr = new Date(att.created_at).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  });
                  return (
                    <div
                      key={att.id || idx}
                      className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 p-3 text-xs"
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-900">{att.topic || "General Topic"}</span>
                          <span className="rounded border border-slate-200 bg-white px-1.5 py-0.5 text-[10px] text-slate-600">
                            {att.subject}
                          </span>
                          <span className="text-[10px] uppercase text-slate-400">{att.difficulty}</span>
                        </div>
                        <p className="mt-1 text-[11px] text-slate-400">{dateStr} • {att.cards_reviewed} cards reviewed</p>
                      </div>
                      <div className="flex items-center gap-2 text-[11px]">
                        <span className="rounded bg-emerald-50 px-2 py-0.5 text-emerald-700 font-semibold border border-emerald-200">🟢 {att.easy_count}</span>
                        <span className="rounded bg-amber-50 px-2 py-0.5 text-amber-800 font-semibold border border-amber-200">🟡 {att.medium_count}</span>
                        <span className="rounded bg-rose-50 px-2 py-0.5 text-rose-700 font-semibold border border-rose-200">🔴 {att.hard_count}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* ==========================================================
            Section: Diagnostics (Strengths & Areas for Improvement)
        ========================================================== */}
        <div className="mt-12 grid gap-6 md:grid-cols-2">

          {/* Strengths */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm">
            <h3 className="font-serif text-lg font-normal text-emerald-700 flex items-center gap-2">
              <span>⭐</span> Key Academic Strengths
            </h3>
            <ul className="mt-4 space-y-2.5 text-sm text-slate-700">
              {analytics?.strengths?.map((str, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-emerald-600 font-bold">•</span>
                  <span>{str}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Areas for Improvement */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm">
            <h3 className="font-serif text-lg font-normal text-[#C59B27] flex items-center gap-2">
              <span>💡</span> Areas for Improvement
            </h3>
            <ul className="mt-4 space-y-2.5 text-sm text-slate-700">
              {analytics?.areas_for_improvement?.map((area, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-[#C59B27] font-bold">•</span>
                  <span>{area}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* ==========================================================
            Section: Learning Goals & Achievements
        ========================================================== */}
        <div className="mt-8 grid gap-6 md:grid-cols-2">
          {/* Learning Goals */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm">
            <h3 className="font-serif text-lg font-normal text-[#C59B27] flex items-center gap-2">
              <span>🎯</span> Targeted Learning Goals
            </h3>
            <ul className="mt-4 space-y-2.5 text-sm text-slate-700">
              {analytics?.learning_goals?.map((goal, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-[#C59B27] font-bold">•</span>
                  <span>{goal}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Achievements */}
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm">
            <h3 className="font-serif text-lg font-normal text-purple-700 flex items-center gap-2">
              <span>🏆</span> Achievement Badges
            </h3>
            <div className="mt-4 space-y-3">
              {analytics?.achievements?.map((ach, idx) => (
                <div
                  key={idx}
                  className={`flex items-center justify-between rounded-xl p-3 border text-xs ${
                    ach.unlocked
                      ? "border-[#C59B27]/40 bg-amber-50/50 text-slate-800"
                      : "border-slate-100 bg-slate-50 text-slate-400 opacity-60"
                  }`}
                >
                  <div>
                    <p className="font-semibold text-sm text-slate-900">{ach.name}</p>
                    <p className="text-slate-600 mt-0.5">{ach.description}</p>
                  </div>
                  <span
                    className={`rounded-full px-2.5 py-1 text-[10px] font-bold ${
                      ach.unlocked
                        ? "border border-emerald-200 bg-emerald-50 text-emerald-700"
                        : "bg-slate-100 text-slate-400"
                    }`}
                  >
                    {ach.unlocked ? "UNLOCKED" : "IN PROGRESS"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

      {/* Study Plan Modal */}
      <StudyPlanModal
        isOpen={isStudyPlanOpen}
        onClose={() => setIsStudyPlanOpen(false)}
        studyPlan={studyPlanData}
        isLoading={isStudyPlanLoading}
        onDownloadPdf={downloadStudyPlanPdf}
        isDownloadingPdf={isDownloadingStudyPlanPdf}
      />
    </main>
  );
}
