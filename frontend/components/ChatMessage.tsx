"use client";

import ComparisonTable from "./ComparisonTable";

interface ComparisonTableData {
  columns: string[];
  rows: string[][];
}

interface ChatMessageData {
  role: "user" | "assistant";
  content: string;
  code?: string;
  comparison_table?: ComparisonTableData;
  audio_url?: string;
}

interface ChatMessageProps {
  message: ChatMessageData;
}

export default function ChatMessage({
  message,
}: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex w-full ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`max-w-3xl rounded-2xl px-5 py-4 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-slate-900 text-slate-200"
        }`}
      >
        {/* Message text */}
        {message.content && (
          <div className="whitespace-pre-wrap leading-7">
            {message.content}
          </div>
        )}

        {/* Play voice button */}
        {!isUser && message.audio_url && (
          <div className="mt-3 flex justify-start">
            <button
              onClick={() => {
                const audio = new Audio(message.audio_url);
                audio.play().catch((err) => console.log("Audio play error:", err));
              }}
              className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-semibold bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700 transition"
            >
              🔊 Play Audio Summary
            </button>
          </div>
        )}

        {/* Code */}
        {!isUser && message.code && (
          <div className="mt-4 overflow-hidden rounded-xl border border-slate-700 bg-slate-950">
            <div className="flex items-center justify-between border-b border-slate-700 bg-slate-900 px-4 py-2">
              <span className="text-xs font-medium text-slate-400">
                Code
              </span>
            </div>

            <pre className="overflow-x-auto p-4 text-sm leading-6 text-slate-200">
              <code>{message.code}</code>
            </pre>
          </div>
        )}

        {/* Comparison Table */}
        {!isUser && message.comparison_table && (
          <div className="mt-4">
            <ComparisonTable
              table={message.comparison_table}
            />
          </div>
        )}
      </div>
    </div>
  );
}