"use client";
import ComparisonTable from "./ComparisonTable";

interface ComparisonTableData {
  columns: string[];
  rows: string[][];
}

interface ChatMessageData {
  role: "user" | "assistant";
  content: string;
  comparison_table?: ComparisonTableData;
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

        {/* Comparison Table */}
        {!isUser && message.comparison_table && (
          <ComparisonTable
            table={message.comparison_table}
          />
        )}
      </div>
    </div>
  );
}