"use client";

import { useState } from "react";

export interface DayPlan {
  day_number: number;
  day_name: string;
  subject: string;
  subject_name: string;
  session_title: string;
  focus_topics: string[];
  learning_activity: string;
  estimated_minutes: number;
  steps: string[];
}

export interface WeakPoint {
  subject: string;
  subject_name: string;
  issue: string;
  example_concept?: string;
  improvement_strategy: string;
  priority_level: string;
}

export interface SubjectRecommendation {
  subject: string;
  subject_name: string;
  status_tier: string;
  quizzes_taken: number;
  quiz_average: number;
  topics_needing_improvement: string[];
  improvement_action: string;
  topics_needing_practice: string[];
  practice_action: string;
  important_revision_topics: string[];
  revision_action: string;
}

export interface StudyTip {
  title: string;
  icon: string;
  description: string;
}

export interface StudyPlanData {
  student_name: string;
  student_email: string;
  generated_date: string;
  target_week: string;
  overall_status: string;
  total_planned_hours: number;
  total_planned_minutes: number;
  primary_focus_subject: string;
  weekly_focus_summary: string;
  priority_weak_points: WeakPoint[];
  subject_wise_recommendations: SubjectRecommendation[];
  day_by_day_plan: DayPlan[];
  actionable_tips: StudyTip[];
}

interface StudyPlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  studyPlan: StudyPlanData | null;
  isLoading: boolean;
  onDownloadPdf: () => Promise<void>;
  isDownloadingPdf: boolean;
}

export default function StudyPlanModal({
  isOpen,
  onClose,
  studyPlan,
  isLoading,
  onDownloadPdf,
  isDownloadingPdf,
}: StudyPlanModalProps) {
  const [activeTab, setActiveTab] = useState<"schedule" | "subjects" | "weakpoints" | "tips">("schedule");
  const [selectedDay, setSelectedDay] = useState<number>(1);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto animate-fadeIn">
      <div className="relative w-full max-w-5xl rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950/80 px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-md shadow-indigo-500/20 text-xl">
              📅
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-white tracking-tight">
                  Personalized Weekly Study Plan
                </h2>
                <span className="rounded-full border border-indigo-500/40 bg-indigo-950/60 px-2.5 py-0.5 text-xs font-semibold text-indigo-300">
                  Targeted Coaching
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Tailored for <span className="text-slate-200 font-medium">{studyPlan?.student_name || "Student"}</span> • Week of {studyPlan?.target_week || "Current Week"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onDownloadPdf}
              disabled={isDownloadingPdf || isLoading}
              className="flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-xs font-bold text-slate-950 hover:bg-slate-200 disabled:opacity-50 transition shadow-sm"
              title="Download official PDF report"
            >
              {isDownloadingPdf ? (
                <>
                  <svg className="h-3.5 w-3.5 animate-spin text-slate-950" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                  </svg>
                  <span>Exporting PDF...</span>
                </>
              ) : (
                <>
                  <span>📄</span>
                  <span>Download PDF Plan</span>
                </>
              )}
            </button>
            <button
              onClick={onClose}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-700 bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white transition"
              aria-label="Close modal"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent"></div>
              <p className="mt-4 text-sm text-slate-400">
                Analyzing quiz error patterns and synthesizing personalized study schedule...
              </p>
            </div>
          ) : !studyPlan ? (
            <div className="text-center py-16">
              <p className="text-rose-400">Unable to load study plan. Please try again.</p>
            </div>
          ) : (
            <>
              {/* Executive Summary Banner */}
              <div className="rounded-xl border border-indigo-900/60 bg-gradient-to-r from-indigo-950/40 via-slate-900/80 to-purple-950/40 p-4 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl mt-0.5">🎯</span>
                    <div>
                      <h3 className="text-sm font-bold text-indigo-300 uppercase tracking-wider">
                        Weekly Focus Strategy
                      </h3>
                      <p className="mt-1 text-sm text-slate-200 leading-relaxed">
                        {studyPlan.weekly_focus_summary}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0 self-start sm:self-center border-t sm:border-t-0 sm:border-l border-slate-800 pt-3 sm:pt-0 sm:pl-4">
                    <div className="text-center">
                      <p className="text-[10px] uppercase font-bold text-slate-400">Commitment</p>
                      <p className="text-lg font-bold text-indigo-400">{studyPlan.total_planned_hours} hrs</p>
                    </div>
                    <div className="text-center">
                      <p className="text-[10px] uppercase font-bold text-slate-400">Primary Focus</p>
                      <p className="text-sm font-semibold text-amber-300 max-w-[130px] truncate">{studyPlan.primary_focus_subject}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-2">
                <button
                  onClick={() => setActiveTab("schedule")}
                  className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                    activeTab === "schedule"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                      : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                  }`}
                >
                  <span>📅</span>
                  <span>7-Day Schedule</span>
                </button>
                <button
                  onClick={() => setActiveTab("weakpoints")}
                  className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                    activeTab === "weakpoints"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                      : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                  }`}
                >
                  <span>💡</span>
                  <span>Weak Points & Remediation</span>
                  {studyPlan.priority_weak_points?.length > 0 && (
                    <span className="ml-1 rounded-full bg-rose-500/80 px-1.5 py-0.2 text-[10px] text-white">
                      {studyPlan.priority_weak_points.length}
                    </span>
                  )}
                </button>
                <button
                  onClick={() => setActiveTab("subjects")}
                  className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                    activeTab === "subjects"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                      : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                  }`}
                >
                  <span>📚</span>
                  <span>Subject-Wise Topic Diagnostics</span>
                </button>
                <button
                  onClick={() => setActiveTab("tips")}
                  className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                    activeTab === "tips"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                      : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                  }`}
                >
                  <span>🧠</span>
                  <span>Study Techniques</span>
                </button>
              </div>

              {/* Tab 1: 7-Day Day-by-Day Schedule */}
              {activeTab === "schedule" && (
                <div className="space-y-4">
                  {/* Days Horizontal Picker */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2">
                    {studyPlan.day_by_day_plan.map((d) => {
                      const isSelected = selectedDay === d.day_number;
                      return (
                        <button
                          key={d.day_number}
                          onClick={() => setSelectedDay(d.day_number)}
                          className={`flex flex-col items-start rounded-xl p-3 text-left transition border ${
                            isSelected
                              ? "border-indigo-500 bg-indigo-950/60 shadow-md shadow-indigo-500/20"
                              : "border-slate-800 bg-slate-900/60 hover:bg-slate-850 hover:border-slate-700"
                          }`}
                        >
                          <span className={`text-[10px] font-bold uppercase tracking-wider ${isSelected ? "text-indigo-300" : "text-slate-400"}`}>
                            {d.day_name.split(" ")[0]}
                          </span>
                          <span className="text-xs font-bold text-white mt-0.5 truncate w-full">
                            {d.day_name.includes("(") ? d.day_name.split("(")[1].replace(")", "") : d.day_name}
                          </span>
                          <span className="mt-2 text-[10px] font-medium text-slate-400 truncate w-full">
                            {d.subject}
                          </span>
                          <span className="mt-1 rounded-md bg-slate-800 px-1.5 py-0.5 text-[9px] font-semibold text-indigo-300">
                            ⏱️ {d.estimated_minutes}m
                          </span>
                        </button>
                      );
                    })}
                  </div>

                  {/* Selected Day Details Card */}
                  {(() => {
                    const currentDay = studyPlan.day_by_day_plan.find((d) => d.day_number === selectedDay) || studyPlan.day_by_day_plan[0];
                    if (!currentDay) return null;
                    return (
                      <div className="rounded-2xl border border-slate-700 bg-slate-900/80 p-6 space-y-4">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="rounded-lg bg-indigo-600/30 border border-indigo-500/40 px-2.5 py-1 text-xs font-bold text-indigo-300">
                                {currentDay.day_name}
                              </span>
                              <span className="rounded-lg bg-slate-800 border border-slate-700 px-2.5 py-1 text-xs font-medium text-slate-300">
                                {currentDay.subject_name} ({currentDay.subject})
                              </span>
                            </div>
                            <h3 className="text-lg font-bold text-white mt-2">
                              {currentDay.session_title}
                            </h3>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="rounded-full bg-slate-800 border border-slate-700 px-3 py-1 text-xs font-semibold text-indigo-300 flex items-center gap-1.5">
                              <span>⏱️ Planned Time:</span>
                              <span className="font-bold text-white">{currentDay.estimated_minutes} mins</span>
                            </span>
                          </div>
                        </div>

                        <div className="grid gap-4 sm:grid-cols-2">
                          <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                              <span>🎯</span> Target Topics
                            </h4>
                            <div className="mt-2.5 flex flex-wrap gap-1.5">
                              {currentDay.focus_topics.map((top, idx) => (
                                <span
                                  key={idx}
                                  className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1 text-xs font-medium text-slate-200"
                                >
                                  {top}
                                </span>
                              ))}
                            </div>
                          </div>

                          <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                              <span>⚡</span> Planned Activity
                            </h4>
                            <p className="mt-2.5 text-xs font-semibold text-emerald-400">
                              {currentDay.learning_activity}
                            </p>
                          </div>
                        </div>

                        <div className="rounded-xl border border-indigo-900/40 bg-indigo-950/20 p-4">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1.5">
                            <span>📋</span> Step-by-Step Study Execution Plan
                          </h4>
                          <ul className="mt-3 space-y-2 text-xs text-slate-300">
                            {currentDay.steps.map((step, idx) => (
                              <li key={idx} className="flex items-start gap-2.5">
                                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-indigo-600/40 text-[10px] font-bold text-indigo-300">
                                  {idx + 1}
                                </span>
                                <span className="leading-relaxed mt-0.5">{step}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    );
                  })()}
                </div>
              )}

              {/* Tab 2: Weak Points & Remediation */}
              {activeTab === "weakpoints" && (
                <div className="space-y-4">
                  <div className="border-b border-slate-800 pb-2">
                    <h3 className="text-sm font-bold text-slate-200">
                      Diagnostics: User Weak Points & Specific How-To-Improve Strategies
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Identified automatically from quiz missed questions, flashcard difficulty flags, and subject accuracy trends.
                    </p>
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    {studyPlan.priority_weak_points.map((wp, idx) => (
                      <div
                        key={idx}
                        className="rounded-xl border border-rose-900/50 bg-slate-900/80 p-5 space-y-3"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-rose-400 font-bold">⚠️</span>
                            <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                              {wp.subject_name} ({wp.subject})
                            </span>
                          </div>
                          <span
                            className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                              wp.priority_level === "High"
                                ? "bg-rose-950 text-rose-400 border border-rose-800"
                                : "bg-amber-950 text-amber-400 border border-amber-800"
                            }`}
                          >
                            {wp.priority_level} Priority
                          </span>
                        </div>

                        <div>
                          <p className="text-sm font-semibold text-white">
                            {wp.issue}
                          </p>
                          {wp.example_concept && (
                            <p className="text-xs text-slate-400 mt-1 italic bg-slate-950/60 p-2 rounded-lg border border-slate-800/80">
                              &ldquo;{wp.example_concept}&rdquo;
                            </p>
                          )}
                        </div>

                        <div className="rounded-lg border border-indigo-900/40 bg-indigo-950/30 p-3">
                          <p className="text-[11px] font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1.5">
                            <span>💡</span> How to Improve & Master This
                          </p>
                          <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                            {wp.improvement_strategy}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 3: Subject-Wise Topic Breakdown (3 Tracks) */}
              {activeTab === "subjects" && (
                <div className="space-y-4">
                  <div className="border-b border-slate-800 pb-2">
                    <h3 className="text-sm font-bold text-slate-200">
                      Subject-Wise Topic Diagnostics (3-Track Learning Matrix)
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Categorized into topics needing improvement, consistent drills, and core high-yield exam revision.
                    </p>
                  </div>

                  <div className="space-y-4">
                    {studyPlan.subject_wise_recommendations.map((rec) => (
                      <div
                        key={rec.subject}
                        className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 space-y-4"
                      >
                        {/* Subject Header */}
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                          <div className="flex items-center gap-2.5">
                            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-900/40 border border-indigo-700/50 text-xs font-bold text-indigo-300">
                              {rec.subject}
                            </span>
                            <div>
                              <h4 className="text-sm font-bold text-white">
                                {rec.subject_name}
                              </h4>
                              <p className="text-[11px] text-slate-400">
                                {rec.quizzes_taken} Quizzes Taken • Average Score: {rec.quiz_average}%
                              </p>
                            </div>
                          </div>
                          <span
                            className={`rounded-full px-2.5 py-0.5 text-[10px] font-semibold border ${
                              rec.status_tier === "Mastery"
                                ? "bg-emerald-950 text-emerald-300 border-emerald-800"
                                : rec.status_tier === "Proficient"
                                ? "bg-sky-950 text-sky-300 border-sky-800"
                                : rec.status_tier === "Developing"
                                ? "bg-amber-950 text-amber-300 border-amber-800"
                                : "bg-rose-950 text-rose-300 border-rose-800"
                            }`}
                          >
                            {rec.status_tier}
                          </span>
                        </div>

                        {/* 3 Tracks Grid */}
                        <div className="grid gap-3 md:grid-cols-3">
                          {/* Track 1: Needs Improvement */}
                          <div className="rounded-xl border border-rose-900/40 bg-rose-950/10 p-3.5 space-y-2">
                            <div className="flex items-center gap-1.5">
                              <span className="text-rose-400 text-xs">🔴</span>
                              <h5 className="text-xs font-bold uppercase tracking-wider text-rose-300">
                                Needs Improvement
                              </h5>
                            </div>
                            <ul className="space-y-1 text-xs text-slate-300">
                              {rec.topics_needing_improvement.map((t, i) => (
                                <li key={i} className="flex items-start gap-1.5">
                                  <span className="text-rose-400">•</span>
                                  <span>{t}</span>
                                </li>
                              ))}
                            </ul>
                            <p className="text-[10px] text-slate-400 pt-1 border-t border-rose-900/30">
                              <span className="font-semibold text-rose-300">Fix:</span> {rec.improvement_action}
                            </p>
                          </div>

                          {/* Track 2: Consistent Practice */}
                          <div className="rounded-xl border border-amber-900/40 bg-amber-950/10 p-3.5 space-y-2">
                            <div className="flex items-center gap-1.5">
                              <span className="text-amber-400 text-xs">🟡</span>
                              <h5 className="text-xs font-bold uppercase tracking-wider text-amber-300">
                                Consistent Practice
                              </h5>
                            </div>
                            <ul className="space-y-1 text-xs text-slate-300">
                              {rec.topics_needing_practice.map((t, i) => (
                                <li key={i} className="flex items-start gap-1.5">
                                  <span className="text-amber-400">•</span>
                                  <span>{t}</span>
                                </li>
                              ))}
                            </ul>
                            <p className="text-[10px] text-slate-400 pt-1 border-t border-amber-900/30">
                              <span className="font-semibold text-amber-300">Drill:</span> {rec.practice_action}
                            </p>
                          </div>

                          {/* Track 3: Important Topics to Revise */}
                          <div className="rounded-xl border border-emerald-900/40 bg-emerald-950/10 p-3.5 space-y-2">
                            <div className="flex items-center gap-1.5">
                              <span className="text-emerald-400 text-xs">🟢</span>
                              <h5 className="text-xs font-bold uppercase tracking-wider text-emerald-300">
                                Important Revision
                              </h5>
                            </div>
                            <ul className="space-y-1 text-xs text-slate-300">
                              {rec.important_revision_topics.map((t, i) => (
                                <li key={i} className="flex items-start gap-1.5">
                                  <span className="text-emerald-400">•</span>
                                  <span>{t}</span>
                                </li>
                              ))}
                            </ul>
                            <p className="text-[10px] text-slate-400 pt-1 border-t border-emerald-900/30">
                              <span className="font-semibold text-emerald-300">Strategy:</span> {rec.revision_action}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 4: Study Techniques */}
              {activeTab === "tips" && (
                <div className="space-y-4">
                  <div className="border-b border-slate-800 pb-2">
                    <h3 className="text-sm font-bold text-slate-200">
                      Cognitive Science Study Habits & Retention Protocols
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Empirically proven techniques to maximize test recall and minimize study fatigue.
                    </p>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    {studyPlan.actionable_tips.map((tip, idx) => (
                      <div
                        key={idx}
                        className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-2"
                      >
                        <div className="flex items-center gap-2.5">
                          <span className="text-2xl">{tip.icon}</span>
                          <h4 className="text-sm font-bold text-white">{tip.title}</h4>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed">
                          {tip.description}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Modal Footer */}
        <div className="border-t border-slate-800 bg-slate-950/90 px-6 py-4 flex items-center justify-between">
          <div className="text-xs text-slate-400">
            <span>Powered by Multi-Agent Academic Diagnostic Engine</span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-800 transition"
            >
              Close
            </button>
            <button
              onClick={onDownloadPdf}
              disabled={isDownloadingPdf || isLoading}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-5 py-2 text-xs font-bold text-white hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 transition shadow-lg shadow-indigo-500/20"
            >
              {isDownloadingPdf ? (
                <>
                  <svg className="h-3.5 w-3.5 animate-spin text-white" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                  </svg>
                  <span>Exporting PDF...</span>
                </>
              ) : (
                <>
                  <span>📄</span>
                  <span>Download Study Plan (PDF)</span>
                </>
              )}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
