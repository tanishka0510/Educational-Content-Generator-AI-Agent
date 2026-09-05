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
  activeChatId: string | null;

  onNewChat: () => void;

  onSelectChat: (
    chat: Chat
  ) => void;

  onDeleteChat?: (
    chatId: string
  ) => void;

  onBack: () => void;
  onOpenDocuments?: () => void;
  documentCount?: number;
  activeDocumentName?: string;
  onUnloadDocument?: () => void;
}


// =====================================================
// Chat Sidebar
// =====================================================

export default function ChatSidebar({
  chats,
  activeChatId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  onBack,
  onOpenDocuments,
  documentCount = 0,
  activeDocumentName,
  onUnloadDocument,
}: ChatSidebarProps) {


  const subjectChats = chats.sort(
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

        {/* Previous Documents Button */}
        {onOpenDocuments && (
          <button
            type="button"
            onClick={onOpenDocuments}
            className="mt-2.5 flex w-full items-center justify-between rounded-xl border border-slate-800 bg-slate-900/90 px-3.5 py-2.5 text-xs font-medium text-slate-300 transition hover:border-sky-500/50 hover:bg-slate-800 hover:text-white group"
          >
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-base group-hover:scale-110 transition-transform">📁</span>
              <span className="truncate">Previous Documents</span>
            </div>
            {documentCount > 0 && (
              <span className="shrink-0 rounded-full bg-sky-950 px-2 py-0.5 text-[10px] font-semibold text-sky-400 border border-sky-800/60">
                {documentCount}
              </span>
            )}
          </button>
        )}

        {/* Active Document Indicator Pill */}
        {activeDocumentName && (
          <div className="mt-2 flex items-center justify-between gap-2 rounded-lg border border-sky-800/40 bg-sky-950/40 px-2.5 py-1.5 text-xs text-sky-300 animate-in fade-in duration-150">
            <div className="flex items-center gap-1.5 min-w-0">
              <span className="shrink-0">📄</span>
              <span className="truncate text-[11px] font-medium" title={activeDocumentName}>
                {activeDocumentName}
              </span>
            </div>
            {onUnloadDocument && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onUnloadDocument();
                }}
                className="shrink-0 text-[10px] text-sky-400 hover:text-rose-300 transition underline cursor-pointer"
              >
                Unload
              </button>
            )}
          </div>
        )}

      </div>

      {/* =================================================
          CHAT HISTORY
      ================================================= */}

      <div className="flex-1 overflow-y-auto p-3">

        <div className="mb-3 px-2 text-xs font-semibold uppercase tracking-wider text-slate-600">

          Chats

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
            {subjectChats.map((chat) => {
              const formattedDate = chat.updatedAt
                ? new Date(chat.updatedAt).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                  })
                : "";

              return (
                <div
                  key={chat.id}
                  onClick={() => onSelectChat(chat)}
                  className={`group relative flex w-full cursor-pointer items-center justify-between rounded-xl px-3 py-2.5 transition ${
                    activeChatId === chat.id
                      ? "bg-slate-800 text-white"
                      : "text-slate-400 hover:bg-slate-900 hover:text-white"
                  }`}
                >
                  <div className="min-w-0 flex-1 pr-2">
                    <div className="truncate text-sm font-medium">
                      {chat.title}
                    </div>
                    <div className="mt-0.5 flex items-center gap-2 text-xs text-slate-500">
                      <span>{chat.messages.length} messages</span>
                      {formattedDate && (
                        <>
                          <span>•</span>
                          <span>{formattedDate}</span>
                        </>
                      )}
                    </div>
                  </div>

                  {onDeleteChat && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm(`Delete session "${chat.title}"?`)) {
                          onDeleteChat(chat.id);
                        }
                      }}
                      title="Delete chat session"
                      className="rounded p-1 text-slate-500 opacity-0 transition hover:bg-rose-950/60 hover:text-rose-400 group-hover:opacity-100"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-3.5 w-3.5"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </button>
                  )}
                </div>
              );
            })}
          </div>


        )}

      </div>

    </aside>
  );
}
