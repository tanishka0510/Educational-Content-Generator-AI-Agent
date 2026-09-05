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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 overflow-y-auto animate-fadeIn font-sans">
      <div className="relative w-full max-w-5xl rounded-2xl border border-slate-200/90 bg-white shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-200/80 bg-white px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-50 border border-[#C59B27]/40 text-[#C59B27] text-xl shadow-sm">
              📅
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-serif text-xl font-bold text-slate-900 tracking-tight">
                  Personalized Weekly Study Plan
                </h2>
                <span className="rounded-full border border-[#C59B27]/40 bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-[#C59B27]">
                  Academic Coach
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Tailored for <span className="text-[#C59B27] font-semibold">{studyPlan?.student_name || "Student"}</span> • Week of {studyPlan?.target_week || "Current Week"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onDownloadPdf}
              disabled={isDownloadingPdf || isLoading}
              className="flex items-center gap-2 rounded-xl bg-[#C59B27] px-4 py-2 text-xs font-bold text-slate-950 hover:bg-[#B38A1F] disabled:opacity-50 transition shadow-sm"
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
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
              aria-label="Close modal"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-[#F8FAFC]">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-[#C59B27] border-t-transparent"></div>
              <p className="mt-4 text-sm text-slate-500">
                Analyzing quiz error patterns and synthesizing personalized study schedule...
              </p>
            </div>
          ) : !studyPlan ? (
            <div className="text-center py-16">
              <p className="text-rose-500 font-medium">Unable to load study plan. Please try again.</p>
            </div>
          ) : (
            <>
              {/* Executive Summary Banner */}
              <div className="rounded-xl border border-[#C59B27]/30 bg-gradient-to-r from-amber-50/90 via-white to-amber-50/70 p-5 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl mt-0.5">🎯</span>
                    <div>
                      <h3 className="text-xs font-bold text-[#C59B27] uppercase tracking-wider">
                        Weekly Focus Strategy
                      </h3>
                      <p className="mt-1 text-sm text-slate-700 leading-relaxed font-medium">
                        {studyPlan.weekly_focus_summary}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 shrink-0 self-start sm:self-center border-t sm:border-t-0 sm:border-l border-slate-200 pt-3 sm:pt-0 sm:pl-4">
                    <div className="text-center">
                      <p className="text-[10px] uppercase font-bold text-slate-400">Commitment</p>
                      <p className="text-lg font-bold text-[#C59B27]">{studyPlan.total_planned_hours} hrs</p>
                    </div>
                    <div className="text-center">
                      <p className="text-[10px] uppercase font-bold text-slate-400">Primary Focus</p>
                      <p className="text-sm font-semibold text-slate-800 max-w-[130px] truncate">{studyPlan.primary_focus_subject}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-2">
                <button
                  onClick={() => setActiveTab("schedule")}
                  className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                    activeTab === "schedule"
                      ? "bg-[#C59B27] text-slate-950 font-bold shadow-sm"
                      : "text-slate-600 hover:bg-white hover:text-slate-900"
                  }`}
                >
                  <span>📅</span>
                  <span>7-Day Schedule</span>
                </button>
                <button
                  onClick={() => setActiveTab("weakpoints")}
                  className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                    activeTab === "weakpoints"
                      ? "bg-[#C59B27] text-slate-950 font-bold shadow-sm"
                      : "text-slate-600 hover:bg-white hover:text-slate-900"
                  }`}
                >
                  <span>💡</span>
                  <span>Weak Points & Remediation</span>
                  {studyPlan.priority_weak_points?.length > 0 && (
                    <span className="ml-1 rounded-full bg-rose-500 px-1.5 py-0.2 text-[10px] text-white">
                      {studyPlan.priority_weak_points.length}
                    </span>
                  )}
                </button>
                <button
                  onClick={() => setActiveTab("subjects")}
                  className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                    activeTab === "subjects"
                      ? "bg-[#C59B27] text-slate-950 font-bold shadow-sm"
                      : "text-slate-600 hover:bg-white hover:text-slate-900"
                  }`}
                >
                  <span>📚</span>
                  <span>Subject-Wise Topic Diagnostics</span>
                </button>
                <button
                  onClick={() => setActiveTab("tips")}
                  className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                    activeTab === "tips"
                      ? "bg-[#C59B27] text-slate-950 font-bold shadow-sm"
                      : "text-slate-600 hover:bg-white hover:text-slate-900"
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
                              ? "border-[#C59B27] bg-amber-50/80 shadow-sm"
                              : "border-slate-200 bg-white hover:border-[#C59B27]/40 hover:bg-slate-50"
                          }`}
                        >
                          <span className={`text-[10px] font-bold uppercase tracking-wider ${isSelected ? "text-[#C59B27]" : "text-slate-400"}`}>
                            {d.day_name.split(" ")[0]}
                          </span>
                          <span className="text-xs font-bold text-slate-850 mt-0.5 truncate w-full text-slate-900">
                            {d.day_name.includes("(") ? d.day_name.split("(")[1].replace(")", "") : d.day_name}
                          </span>
                          <span className="mt-2 text-[10px] font-medium text-slate-500 truncate w-full">
                            {d.subject}
                          </span>
                          <span className="mt-1 rounded-md bg-slate-100 px-1.5 py-0.5 text-[9px] font-semibold text-slate-700">
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
                      <div className="rounded-2xl border border-slate-200/90 bg-white p-6 space-y-4 shadow-sm">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-4">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="rounded-lg bg-amber-50 border border-[#C59B27]/30 px-2.5 py-1 text-xs font-bold text-[#C59B27]">
                                {currentDay.day_name}
                              </span>
                              <span className="rounded-lg bg-slate-100 border border-slate-200 px-2.5 py-1 text-xs font-medium text-slate-700">
                                {currentDay.subject_name} ({currentDay.subject})
                              </span>
                            </div>
                            <h3 className="text-lg font-bold text-slate-900 mt-2">
                              {currentDay.session_title}
                            </h3>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="rounded-full bg-slate-50 border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-700 flex items-center gap-1.5 shadow-sm">
                              <span>⏱️ Planned Time:</span>
                              <span className="font-bold text-slate-900">{currentDay.estimated_minutes} mins</span>
                            </span>
                          </div>
                        </div>

                        <div className="grid gap-4 sm:grid-cols-2">
                          <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                              <span>🎯</span> Target Topics
                            </h4>
                            <div className="mt-2.5 flex flex-wrap gap-1.5">
                              {currentDay.focus_topics.map((top, idx) => (
                                <span
                                  key={idx}
                                  className="rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium text-slate-750 text-slate-800 shadow-2xs"
                                >
                                  {top}
                                </span>
                              ))}
                            </div>
                          </div>

                          <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                              <span>⚡</span> Planned Activity
                            </h4>
                            <p className="mt-2.5 text-xs font-semibold text-emerald-700">
                              {currentDay.learning_activity}
                            </p>
                          </div>
                        </div>

                        <div className="rounded-xl border border-[#C59B27]/30 bg-amber-50/30 p-4">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-[#C59B27] flex items-center gap-1.5">
                            <span>📋</span> Step-by-Step Study Execution Plan
                          </h4>
                          <ul className="mt-3 space-y-2 text-xs text-slate-700">
                            {currentDay.steps.map((step, idx) => (
                              <li key={idx} className="flex items-start gap-2.5">
                                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-amber-100 text-[10px] font-bold text-[#C59B27]">
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
                  <div className="border-b border-slate-200 pb-2">
                    <h3 className="text-sm font-bold text-slate-900">
                      Diagnostics: User Weak Points & Specific How-To-Improve Strategies
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Identified automatically from quiz missed questions, flashcard difficulty flags, and subject accuracy trends.
                    </p>
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    {studyPlan.priority_weak_points.map((wp, idx) => (
                      <div
                        key={idx}
                        className="rounded-xl border border-slate-200/90 bg-white p-5 space-y-3 shadow-sm"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-rose-500 font-bold">⚠️</span>
                            <span className="text-xs font-bold uppercase tracking-wider text-slate-800">
                              {wp.subject_name} ({wp.subject})
                            </span>
                          </div>
                          <span
                            className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                              wp.priority_level === "High"
                                ? "bg-rose-50 text-rose-700 border border-rose-200"
                                : "bg-amber-50 text-amber-700 border border-amber-200"
                            }`}
                          >
                            {wp.priority_level} Priority
                          </span>
                        </div>

                        <div>
                          <p className="text-sm font-semibold text-slate-900">
                            {wp.issue}
                          </p>
                          {wp.example_concept && (
                            <p className="text-xs text-slate-600 mt-1 italic bg-slate-50 p-2 rounded-lg border border-slate-200">
                              &ldquo;{wp.example_concept}&rdquo;
                            </p>
                          )}
                        </div>

                        <div className="rounded-lg border border-[#C59B27]/30 bg-amber-50/40 p-3">
                          <p className="text-[11px] font-bold uppercase tracking-wider text-[#C59B27] flex items-center gap-1.5">
                            <span>💡</span> How to Improve & Master This
                          </p>
                          <p className="text-xs text-slate-700 mt-1 leading-relaxed">
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
                  <div className="border-b border-slate-200 pb-2">
                    <h3 className="text-sm font-bold text-slate-900">
                      Subject-Wise Topic Diagnostics (3-Track Learning Matrix)
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Categorized into topics needing improvement, consistent drills, and core high-yield exam revision.
                    </p>
                  </div>

                  <div className="space-y-4">
                    {studyPlan.subject_wise_recommendations.map((rec) => (
                      <div
                        key={rec.subject}
                        className="rounded-2xl border border-slate-200/90 bg-white p-5 space-y-4 shadow-sm"
                      >
                        {/* Subject Header */}
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-3">
                          <div className="flex items-center gap-2.5">
                            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50 border border-[#C59B27]/40 text-xs font-bold text-[#C59B27]">
                              {rec.subject}
                            </span>
                            <div>
                              <h4 className="text-sm font-bold text-slate-900">
                                {rec.subject_name}
                              </h4>
                              <p className="text-[11px] text-slate-500">
                                {rec.quizzes_taken} Quizzes Taken • Average Score: {rec.quiz_average}%
                              </p>
                            </div>
                          </div>
                          <span
                            className={`rounded-full px-2.5 py-0.5 text-[10px] font-semibold border ${
                              rec.status_tier === "Mastery"
                                ? "bg-emerald-50 text-emerald-700 border-emerald-300"
                                : rec.status_tier === "Proficient"
                                ? "bg-sky-50 text-sky-700 border-sky-300"
                                : rec.status_tier === "Developing"
                                ? "bg-amber-50 text-amber-700 border-amber-300"
                                : "bg-rose-50 text-rose-700 border-rose-300"
                            }`}
                          >
                            {rec.status_tier}
                          </span>
                        </div>

                        {/* 3 Tracks Grid */}
                        <div className="grid gap-3 md:grid-cols-3">
                          {/* Track 1: Needs Improvement */}
                          <div className="rounded-xl border border-rose-200 bg-rose-50/50 p-3.5 space-y-2">
                            <div className="flex items-center gap-1.5">
                              <span className="text-rose-500 text-xs">🔴</span>
                              <h5 className="text-xs font-bold uppercase tracking-wider text-rose-700">
                                Needs Improvement
                              </h5>
                            </div>
                            <ul className="space-y-1 text-xs text-slate-700">
                              {rec.topics_needing_improvement.map((t, i) => (
                                <li key={i} className="flex items-start gap-1.5">
                                  <span className="text-rose-500">•</span>
                                  <span>{t}</span>
                                </li>
                              ))}
                            </ul>
                            <p className="text-[10px] text-slate-600 pt-1 border-t border-rose-200">
                              <span className="font-semibold text-rose-700">Fix:</span> {rec.improvement_action}
                            </p>
                          </div>

                          {/* Track 2: Consistent Practice */}
                          <div className="rounded-xl border border-amber-200 bg-amber-50/50 p-3.5 space-y-2">
                            <div className="flex items-center gap-1.5">
                              <span className="text-amber-500 text-xs">🟡</span>
                              <h5 className="text-xs font-bold uppercase tracking-wider text-amber-800">
                                Consistent Practice
                              </h5>
                            </div>
                            <ul className="space-y-1 text-xs text-slate-700">
                              {rec.topics_needing_practice.map((t, i) => (
                                <li key={i} className="flex items-start gap-1.5">
                                  <span className="text-amber-600">•</span>
                                  <span>{t}</span>
                                </li>
                              ))}
                            </ul>
                            <p className="text-[10px] text-slate-600 pt-1 border-t border-amber-200">
                              <span className="font-semibold text-amber-800">Drill:</span> {rec.practice_action}
                            </p>
                          </div>

                          {/* Track 3: Important Topics to Revise */}
                          <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-3.5 space-y-2">
                            <div className="flex items-center gap-1.5">
                              <span className="text-emerald-600 text-xs">🟢</span>
                              <h5 className="text-xs font-bold uppercase tracking-wider text-emerald-700">
                                Important Revision
                              </h5>
                            </div>
                            <ul className="space-y-1 text-xs text-slate-700">
                              {rec.important_revision_topics.map((t, i) => (
                                <li key={i} className="flex items-start gap-1.5">
                                  <span className="text-emerald-600">•</span>
                                  <span>{t}</span>
                                </li>
                              ))}
                            </ul>
                            <p className="text-[10px] text-slate-600 pt-1 border-t border-emerald-200">
                              <span className="font-semibold text-emerald-700">Strategy:</span> {rec.revision_action}
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
                  <div className="border-b border-slate-200 pb-2">
                    <h3 className="text-sm font-bold text-slate-900">
                      Cognitive Science Study Habits & Retention Protocols
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Empirically proven techniques to maximize test recall and minimize study fatigue.
                    </p>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    {studyPlan.actionable_tips.map((tip, idx) => (
                      <div
                        key={idx}
                        className="rounded-xl border border-slate-200/90 bg-white p-5 space-y-2 shadow-sm"
                      >
                        <div className="flex items-center gap-2.5">
                          <span className="text-2xl">{tip.icon}</span>
                          <h4 className="text-sm font-bold text-slate-900">{tip.title}</h4>
                        </div>
                        <p className="text-xs text-slate-600 leading-relaxed">
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
        <div className="border-t border-slate-200 bg-slate-50 px-6 py-4 flex items-center justify-between">
          <div className="text-xs text-slate-500">
            <span>Powered by Multi-Agent Academic Diagnostic Engine</span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition shadow-sm"
            >
              Close
            </button>
            <button
              onClick={onDownloadPdf}
              disabled={isDownloadingPdf || isLoading}
              className="flex items-center gap-2 rounded-xl bg-[#C59B27] px-5 py-2 text-xs font-bold text-slate-950 hover:bg-[#B38A1F] disabled:opacity-50 transition shadow-sm"
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
