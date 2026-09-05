"use client";

import React, { useState, useEffect } from "react";

export interface UploadedDocument {
  id: number;
  user_id?: number;
  filename: string;
  file_type: string;
  file_size?: number;
  subject: string;
  topic?: string;
  chunks_count?: number;
  status: string;
  created_at: string;
}


const baseUrl =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface DocumentsModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeDocumentName: string;
  onSelectDocument: (doc: UploadedDocument) => void;
  onUnloadDocument: () => void;
}

export default function DocumentsModal({
  isOpen,
  onClose,
  activeDocumentName,
  onSelectDocument,
  onUnloadDocument,
}: DocumentsModalProps) {
  const [documents, setDocuments] = useState<UploadedDocument[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    const token = localStorage.getItem("authToken");
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    try {
      const res = await fetch(`${baseUrl}/upload/documents`, { headers });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          setDocuments(data);
        }
      }
    } catch (err) {
      console.error("Failed to fetch documents:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchDocuments();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleDelete = async (docId: number, filename: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Are you sure you want to delete "${filename}" from your study materials?`)) {
      return;
    }

    setDeletingId(docId);
    const token = localStorage.getItem("authToken");
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    try {
      const res = await fetch(`${baseUrl}/upload/documents/${docId}`, {
        method: "DELETE",
        headers,
      });
      if (res.ok) {
        setDocuments((prev) => prev.filter((d) => d.id !== docId));
        if (activeDocumentName === filename) {
          onUnloadDocument();
        }
      }
    } catch (err) {
      console.error("Failed to delete document:", err);
    } finally {
      setDeletingId(null);
    }
  };

  const filteredDocs = documents;

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "Unknown size";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-sm animate-in fade-in duration-200 font-sans">
      <div className="flex max-h-[85vh] w-full max-w-2xl flex-col rounded-2xl border border-slate-200/80 bg-white shadow-2xl overflow-hidden">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-200/80 bg-white px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-[#C59B27] border border-[#C59B27]/30">
              <span className="text-xl">📁</span>
            </div>
            <div>
              <h2 className="font-serif text-lg font-bold text-slate-900">Previous Study Documents</h2>
              <p className="text-xs text-slate-500">
                Already indexed study materials. Select any file to resume Q&A without re-uploading.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
          >
            ✕
          </button>
        </div>

        {/* Modal Body - Documents List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-3 bg-[#F8FAFC]">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500">
              <div className="h-7 w-7 animate-spin rounded-full border-2 border-[#C59B27] border-t-transparent mb-3" />
              <p className="text-sm">Loading processed study documents...</p>
            </div>
          ) : filteredDocs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center bg-white rounded-xl border border-slate-200 p-8">
              <div className="mb-3 text-4xl">📄</div>
              <h3 className="text-sm font-semibold text-slate-800">
                No processed documents found in your library
              </h3>
              <p className="mt-1 max-w-sm text-xs text-slate-500">
                Upload a document (PDF, TXT, DOCX) via the chat to index it. It will be saved here for instant reuse anytime!
              </p>
            </div>
          ) : (
            filteredDocs.map((doc) => {
              const isActive = activeDocumentName === doc.filename;
              const formattedDate = doc.created_at
                ? new Date(doc.created_at).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })
                : "Saved";

              return (
                <div
                  key={doc.id}
                  className={`group relative flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-xl border p-4 transition ${
                    isActive
                      ? "border-[#C59B27] bg-amber-50/60 shadow-sm"
                      : "border-slate-200/90 bg-white hover:border-[#C59B27]/50 hover:shadow-sm"
                  }`}
                >
                  {/* Document Info */}
                  <div className="flex items-start gap-3 min-w-0 flex-1">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-lg border border-slate-200">
                      📄
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="truncate text-sm font-semibold text-slate-900" title={doc.filename}>
                          {doc.filename}
                        </h4>
                        {isActive && (
                          <span className="shrink-0 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 border border-emerald-300">
                            Active in Chat
                          </span>
                        )}
                      </div>

                      <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                        <span className="rounded border border-[#C59B27]/40 bg-amber-50 px-1.5 py-0.5 text-[10px] font-bold text-[#C59B27]">
                          {doc.subject}
                        </span>
                        <span>•</span>
                        <span>{formatFileSize(doc.file_size)}</span>
                        {doc.chunks_count ? (
                          <>
                            <span>•</span>
                            <span className="text-[#C59B27] font-medium">{doc.chunks_count} chunks</span>
                          </>
                        ) : null}
                        <span>•</span>
                        <span>{formattedDate}</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 sm:self-center shrink-0">
                    {isActive ? (
                      <button
                        type="button"
                        onClick={() => {
                          onUnloadDocument();
                          onClose();
                        }}
                        className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition"
                      >
                        Unload
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={() => {
                          onSelectDocument(doc);
                          onClose();
                        }}
                        className="rounded-lg bg-[#C59B27] hover:bg-[#B38A1F] px-3.5 py-1.5 text-xs font-bold text-slate-950 transition flex items-center gap-1.5 shadow-sm"
                      >
                        <span>⚡</span>
                        <span>Use Document</span>
                      </button>
                    )}

                    <button
                      type="button"
                      onClick={(e) => handleDelete(doc.id, doc.filename, e)}
                      disabled={deletingId === doc.id}
                      title="Delete document"
                      className="rounded-lg p-1.5 text-slate-400 hover:bg-rose-50 hover:text-rose-600 transition disabled:opacity-40"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-6 py-4 text-xs text-slate-500">
          <p>
            💡 Documents are saved in ChromaDB & database for instant question answering.
          </p>
          <button
            onClick={onClose}
            className="rounded-lg border border-slate-200 bg-white px-4 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100 transition shadow-sm"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
