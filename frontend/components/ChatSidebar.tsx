"use client";

// =====================================================
// Types
// =====================================================

interface Message {
  role: "user" | "assistant";
  content?: string;
  comparison_table?: {
    columns: string[];
    rows: string[][];
  };
}

interface Chat {
  id: string;
  subject: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

interface ChatSidebarProps {
  chats: Chat[];
  currentSubject: string;
  activeChatId: string | null;

  onNewChat: () => void;

  onSelectChat: (
    chat: Chat
  ) => void;

  onBack: () => void;
}

// =====================================================
// Subject Names
// =====================================================

function getSubjectName(
  subject: string
): string {

  switch (subject) {

    case "OS":
      return "Operating System";

    case "OOP":
      return "Object Oriented Programming";

    case "CNS":
      return "Cryptography and Network Security";

    case "DBMS":
      return "Database Management System";

    case "SE":
      return "Software Engineering";

    case "AI":
      return "Artificial Intelligence";

    case "ETC":
      return "Effective Technical Communication";

    case "COA":
      return "Computer Organization and Architecture";

    case "DATA STRUCTURE":
      return "Data Structure";

    default:
      return subject;
  }
}

// =====================================================
// Chat Sidebar
// =====================================================

export default function ChatSidebar({
  chats,
  currentSubject,
  activeChatId,
  onNewChat,
  onSelectChat,
  onBack,
}: ChatSidebarProps) {

  // ===================================================
  // Filter Chats By Current Subject
  // ===================================================

  const subjectChats =
    chats
      .filter(
        (chat) =>
          chat.subject ===
          currentSubject
      )
      .sort(
        (a, b) =>
          new Date(
            b.updatedAt
          ).getTime() -
          new Date(
            a.updatedAt
          ).getTime()
      );

  return (

    <aside className="flex w-72 flex-shrink-0 flex-col border-r border-slate-800 bg-slate-950">

      {/* =================================================
          SIDEBAR HEADER
      ================================================= */}

      <div className="border-b border-slate-800 p-4">

        {/* Back Button */}

        <button
          onClick={onBack}
          className="mb-4 flex items-center gap-2 text-sm text-slate-500 transition hover:text-white"
        >

          <span>
            ←
          </span>

          <span>
            Home
          </span>

        </button>

        {/* Application Name */}

        <div className="mb-4">

          <h2 className="font-semibold text-white">
            Educational AI
          </h2>

          <p className="mt-1 text-xs text-slate-500">
            {getSubjectName(
              currentSubject
            )}
          </p>

        </div>

        {/* New Chat */}

        <button
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
        >

          <span className="text-lg">
            +
          </span>

          <span>
            New Chat
          </span>

        </button>

      </div>

      {/* =================================================
          CHAT HISTORY
      ================================================= */}

      <div className="flex-1 overflow-y-auto p-3">

        <div className="mb-3 px-2 text-xs font-semibold uppercase tracking-wider text-slate-600">

          {getSubjectName(
            currentSubject
          )}

          {" "}Chats

        </div>

        {/* =================================================
            No Chats
        ================================================= */}

        {subjectChats.length === 0 ? (

          <div className="px-3 py-8 text-center">

            <div className="mb-3 text-2xl">
              💬
            </div>

            <p className="text-sm text-slate-500">
              No chats yet
            </p>

            <p className="mt-1 text-xs text-slate-600">
              Start a new conversation.
            </p>

          </div>

        ) : (

          // =================================================
          // Chat List
          // =================================================

          <div className="space-y-1">

            {subjectChats.map(
              (chat) => (

                <button
                  key={chat.id}
                  onClick={() =>
                    onSelectChat(
                      chat
                    )
                  }
                  className={`w-full rounded-xl px-3 py-3 text-left transition ${
                    activeChatId ===
                    chat.id
                      ? "bg-slate-800 text-white"
                      : "text-slate-400 hover:bg-slate-900 hover:text-white"
                  }`}
                >

                  {/* Chat Title */}

                  <div className="truncate text-sm font-medium">
                    {chat.title}
                  </div>

                  {/* Message Count */}

                  <div className="mt-1 text-xs text-slate-600">

                    {chat.messages.length}{" "}
                    messages

                  </div>

                </button>

              )
            )}

          </div>

        )}

      </div>

      {/* =================================================
          CURRENT SUBJECT
      ================================================= */}

      <div className="border-t border-slate-800 p-4">

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-3">

          <p className="text-xs text-slate-600">
            Current Subject
          </p>

          <p className="mt-1 text-sm font-medium text-slate-300">
            {getSubjectName(
              currentSubject
            )}
          </p>

        </div>

      </div>

    </aside>
  );
}