"use client";

import { useEffect, useRef, useState } from "react";
import ChatSidebar from "@/components/ChatSidebar";
import ChatMessage from "@/components/ChatMessage";

// =====================================================
// Types
// =====================================================

interface ComparisonTableData {
  columns: string[];
  rows: string[][];
}

interface ChatResponse {
  summary?: string;
  answer?: string;
  comparison_table?: ComparisonTableData;
  learning_objectives?: string[];
  keywords?: string[];
  concepts?: string[];
  difficulty?: string;
  topic?: string;
  intent?: string;
  response_style?: string;
  unit?: string;
  code?: string;
  retrieval_score?: number;
  sources?: string[];
}

interface UploadResponse {
  message?: string;
  filename?: string;
  file_name?: string;
  file_type?: string;
  status?: string;
  success?: boolean;
  chunks_created?: number;
  embedding_dimension?: number;
}

interface Message {
  role: "user" | "assistant";
  content?: string;
  code?: string;
  comparison_table?: ComparisonTableData;
}

interface Chat {
  id: string;
  subject: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

// =====================================================
// Props
// =====================================================

interface ChatPageProps {
  subject: string;
  onBack: () => void;
}

// =====================================================
// Storage Keys
// =====================================================

const STORAGE_KEY =
  "educational-content-generator-chats";

const SUBJECT_STORAGE_KEY =
  "educational-content-generator-selected-subject";

// =====================================================
// Backend URLs
// =====================================================

const BACKEND_URL =
  "http://127.0.0.1:8000";

const PROCESS_CONTENT_URL =
  `${BACKEND_URL}/process-content`;

const UPLOAD_URL =
  `${BACKEND_URL}/upload/`;

// =====================================================
// Subject Names
// =====================================================

const SUBJECT_NAMES: Record<string, string> = {
  OS: "Operating System",
  DBMS: "Database Management System",
  OOP: "Object Oriented Programming",
  COA: "Computer Organization and Architecture",
  AI: "Artificial Intelligence",
  ETC: "Effective Technical Communication",
  "DATA STRUCTURE": "Data Structure",
  CNS: "Cryptography and Network Security",
  SE: "Software Engineering",
};

// =====================================================
// Default Questions
// =====================================================

const DEFAULT_QUESTIONS: Record<string, string[]> = {
  OS: [
    "Compare Process and Thread",
    "Explain Process",
    "Explain Thread",
  ],

  DBMS: [
    "Compare Primary Key and Foreign Key",
    "Explain Normalization",
    "Explain SQL JOIN",
  ],

  OOP: [
    "Compare Inheritance and Polymorphism",
    "Explain Encapsulation",
    "Explain Abstraction",
  ],

  COA: [
    "Compare RISC and CISC",
    "Explain Cache Memory",
    "Explain Pipelining",
  ],

  AI: [
    "Compare Supervised and Unsupervised Learning",
    "Explain Artificial Neural Network",
    "Explain Machine Learning",
  ],

  ETC: [
    "Compare Formal and Informal Communication",
    "Explain Communication Process",
    "Explain Barriers to Communication",
  ],

  "DATA STRUCTURE": [
    "Compare Array and Linked List",
    "Explain Stack",
    "Explain Binary Search Tree",
  ],

  CNS: [
    "Compare Symmetric and Asymmetric Encryption",
    "Explain RSA Algorithm",
    "Explain Digital Signature",
  ],

  SE: [
    "Compare Waterfall and Agile Model",
    "Explain Software Development Life Cycle",
    "Explain Software Testing",
  ],
};

// =====================================================
// Generate Chat ID
// =====================================================

function generateChatId(): string {
  return (
    Date.now().toString() +
    "-" +
    Math.random().toString(36).substring(2, 9)
  );
}

// =====================================================
// Generate Chat Title
// =====================================================

function generateChatTitle(question: string): string {
  const cleanQuestion = question.trim();

  if (cleanQuestion.length <= 45) {
    return cleanQuestion;
  }

  return cleanQuestion.substring(0, 45) + "...";
}

// =====================================================
// Chat Page
// =====================================================

export default function ChatPage({
  subject,
  onBack,
}: ChatPageProps) {
  // ===================================================
  // Current Question
  // ===================================================

  const [question, setQuestion] =
    useState<string>("");

  // ===================================================
  // Current Messages
  // ===================================================

  const [messages, setMessages] =
    useState<Message[]>([]);

  // ===================================================
  // Loading
  // ===================================================

  const [loading, setLoading] =
    useState<boolean>(false);

  // ===================================================
  // All Saved Chats
  // ===================================================

  const [chats, setChats] =
    useState<Chat[]>([]);

  // ===================================================
  // Active Chat
  // ===================================================

  const [activeChatId, setActiveChatId] =
    useState<string | null>(null);

  // ===================================================
  // Uploaded Document
  // ===================================================

  const [uploadedFile, setUploadedFile] =
    useState<File | null>(null);

  const [documentUploaded, setDocumentUploaded] =
    useState<boolean>(false);

  const [uploading, setUploading] =
    useState<boolean>(false);

  const [uploadError, setUploadError] =
    useState<string>("");

  // ===================================================
  // Hidden File Input Reference
  // ===================================================

  const fileInputRef =
    useRef<HTMLInputElement | null>(null);

  // ===================================================
  // Current Subject Name
  // ===================================================

  const subjectName =
    SUBJECT_NAMES[subject] || subject;

  // ===================================================
  // Current Subject Default Questions
  // ===================================================

  const defaultQuestions =
    DEFAULT_QUESTIONS[subject] || [];

  // ===================================================
  // Load Saved Chats
  // ===================================================

  // Voice Recording state
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

  // ===================================================
  // Load Saved Chats
  // ===================================================

  useEffect(() => {
    const fetchChats = async () => {
      const token = localStorage.getItem("authToken");
      if (token) {
        try {
          const response = await fetch(`http://127.0.0.1:8000/chats?subject=${subject}`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          if (response.ok) {
            const backendChats = await response.json();
            setChats(backendChats);
            return;
          }
        } catch (err) {
          console.error("Failed to load chats from backend db, falling back to local storage:", err);
        }
      }

      try {
        const savedChats = localStorage.getItem(STORAGE_KEY);
        if (savedChats) {
          const parsedChats = JSON.parse(savedChats);
          if (Array.isArray(parsedChats)) {
            setChats(parsedChats as Chat[]);
          }
        }
      } catch (error) {
        console.error("Could not load saved chats:", error);
      }
    };

    fetchChats();
  }, [subject]);

  // ===================================================
  // Save Chats (local only if not authenticated)
  // ===================================================

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (token) return; // DB handles storage when logged in

    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(chats)
      );
    } catch (error) {
      console.error(
        "Could not save chats:",
        error
      );
    }
  }, [chats]);

  // ===================================================
  // Save Current Subject
  // ===================================================

  useEffect(() => {
    try {
      localStorage.setItem(
        SUBJECT_STORAGE_KEY,
        subject
      );
    } catch (error) {
      console.error(
        "Could not save selected subject:",
        error
      );
    }
  }, [subject]);

  // ===================================================
  // Create New Chat
  // ===================================================

  const handleNewChat = (): void => {
    setMessages([]);
    setQuestion("");
    setActiveChatId(null);
  };

  // ===================================================
  // Select Existing Chat
  // ===================================================

  const handleSelectChat = (
    chat: Chat
  ): void => {
    setActiveChatId(chat.id);
    setMessages(chat.messages);
    setQuestion("");
  };

  // ===================================================
  // Open File Picker
  // ===================================================

  const handleOpenFilePicker = (): void => {
    if (uploading || loading) {
      return;
    }

    fileInputRef.current?.click();
  };

  // ===================================================
  // Upload Document
  // ===================================================

  const handleFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ): Promise<void> => {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    // =================================================
    // Clear Previous Error
    // =================================================

    setUploadError("");

    // =================================================
    // Supported File Extensions
    // =================================================

    const allowedExtensions = [
      // Documents
      ".pdf",
      ".doc",
      ".docx",
      ".ppt",
      ".pptx",
      ".txt",
      ".md",

      // Images
      ".png",
      ".jpg",
      ".jpeg",
      ".bmp",
      ".tiff",

      // Audio
      ".wav",
      ".mp3",
      ".m4a",
    ];

    const fileName =
      file.name.toLowerCase();

    const isAllowed =
      allowedExtensions.some(
        (extension) =>
          fileName.endsWith(extension)
      );

    if (!isAllowed) {
      setUploadError(
        "Unsupported file type. Please upload PDF, DOC, DOCX, PPT, PPTX, TXT, MD, image, or audio files."
      );

      event.target.value = "";
      return;
    }

    // =================================================
    // Start Upload
    // =================================================

    setUploading(true);

    try {
      const formData =
        new FormData();

      // =================================================
      // IMPORTANT
      //
      // Backend upload endpoint expects:
      //
      // subject: Form(...)
      // file: UploadFile = File(...)
      //
      // Therefore BOTH fields must be sent.
      // =================================================

      formData.append(
        "subject",
        subject
      );

      formData.append(
        "file",
        file
      );

      console.log(
        "Uploading file:",
        file.name
      );

      console.log(
        "Selected subject:",
        subject
      );

      // =================================================
      // Send File To Backend
      // =================================================

      const response =
        await fetch(
          UPLOAD_URL,
          {
            method: "POST",
            body: formData,
          }
        );

      // =================================================
      // Handle Backend Error
      // =================================================

      if (!response.ok) {
        let errorMessage =
          `Upload failed: ${response.status}`;

        try {
          const errorData =
            await response.json();

          console.error(
            "Upload error response:",
            errorData
          );

          if (
            typeof errorData?.detail ===
            "string"
          ) {
            errorMessage =
              errorData.detail;
          }
        } catch {
          // Keep default error message.
        }

        throw new Error(
          errorMessage
        );
      }

      // =================================================
      // Parse Successful Response
      // =================================================

      const data: UploadResponse =
        await response.json();

      console.log(
        "Document upload response:",
        data
      );

      // =================================================
      // Upload Successful
      // =================================================

      setUploadedFile(file);

      setDocumentUploaded(true);

      setUploadError("");

      // =================================================
      // Start Fresh Chat For Uploaded Document
      // =================================================

      setMessages([]);

      setQuestion("");

      setActiveChatId(null);

    } catch (error) {
      console.error(
        "Error uploading document:",
        error
      );

      setDocumentUploaded(false);

      setUploadedFile(null);

      if (
        error instanceof Error
      ) {
        setUploadError(
          error.message
        );
      } else {
        setUploadError(
          "Could not upload the document."
        );
      }

    } finally {
      setUploading(false);

      // Allow selecting the same file again.
      event.target.value = "";
    }
  };

  // ===================================================
  // Remove Uploaded Document
  // ===================================================

  const handleRemoveDocument = (): void => {
    if (
      loading ||
      uploading
    ) {
      return;
    }

    setUploadedFile(null);

    setDocumentUploaded(false);

    setUploadError("");

    // Start a new normal subject chat.
    setMessages([]);

    setQuestion("");

    setActiveChatId(null);
  };

  // ===================================================
  // Send Message
  // ===================================================

  const startRecording = async (): Promise<void> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: "audio/wav" });
        await sendVoiceMessage(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access error:", err);
      alert("Microphone access is denied or unsupported on this browser.");
    }
  };

  const stopRecording = (): void => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const sendVoiceMessage = async (audioBlob: Blob): Promise<void> => {
    setLoading(true);

    const tempUserMsg: Message = {
      role: "user",
      content: "🎤 [Voice Message sending...]",
    };

    const updatedMessages = [...messages, tempUserMsg];
    setMessages(updatedMessages);

    try {
      const token = localStorage.getItem("authToken");
      const headers: Record<string, string> = {};
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const formData = new FormData();
      formData.append("file", audioBlob, "recording.wav");
      formData.append("subject", subject);
      if (activeChatId) {
        formData.append("session_id", activeChatId);
      }
      formData.append("document_uploaded", String(documentUploaded));

      const response = await fetch("http://127.0.0.1:8000/voice/qa", {
        method: "POST",
        headers,
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Voice Q&A Error: ${response.status}`);
      }

      const data = await response.json();

      const finalUserMsg: Message = {
        role: "user",
        content: `🎤 ${data.transcript}`,
      };

      const assistantMsg: Message = {
        role: "assistant",
        content: data.answer,
        audio_url: data.audio_url,
        comparison_table: data.comparison_table,
        code: data.code,
      };

      const finalMessages = [...messages, finalUserMsg, assistantMsg];
      setMessages(finalMessages);

      if (data.audio_url) {
        const audio = new Audio(data.audio_url);
        audio.play().catch((err) => console.log("Autoplay blocked by browser:", err));
      }

      const resolvedSessionId = data.session_id;

      if (activeChatId) {
        setChats((previousChats) =>
          previousChats.map((chat) =>
            chat.id === activeChatId
              ? { ...chat, messages: finalMessages, updatedAt: new Date().toISOString() }
              : chat
          )
        );
      } else {
        const newChat: Chat = {
          id: resolvedSessionId,
          subject,
          title: data.transcript.substring(0, 45) + (data.transcript.length > 45 ? "..." : ""),
          messages: finalMessages,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        setChats((previousChats) => [newChat, ...previousChats]);
        setActiveChatId(resolvedSessionId);
      }
    } catch (err) {
      console.error(err);
      setMessages([
        ...updatedMessages,
        { role: "assistant", content: "Sorry, I could not process your spoken voice query." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // ===================================================
  // Send Message
  // ===================================================

  const sendMessage = async (): Promise<void> => {
    if (!question.trim() || loading || uploading) {
      return;
    }

    const userQuestion = question.trim();
    setQuestion("");

    const userMessage: Message = {
      role: "user",
      content: userQuestion,
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setLoading(true);

    try {
      const token = localStorage.getItem("authToken");
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(PROCESS_CONTENT_URL, {
        method: "POST",
        headers,
        body: JSON.stringify({
          subject,
          question: userQuestion,
          document_uploaded: documentUploaded,
          session_id: activeChatId,
        }),
      });

      if (!response.ok) {
        let errorMessage = `Backend error: ${response.status}`;
        try {
          const errorData = await response.json();
          if (typeof errorData?.detail === "string") {
            errorMessage = errorData.detail;
          }
        } catch {}
        throw new Error(errorMessage);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer || data.summary || "I could not generate an answer.",
        code: data.code,
        comparison_table: data.comparison_table,
        audio_url: data.audio_url,
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);

      if (data.audio_url) {
        const audio = new Audio(data.audio_url);
        audio.play().catch((err) => console.log("Voice reply autoplay blocked:", err));
      }

      const resolvedSessionId = data.session_id || activeChatId;

      if (activeChatId) {
        setChats((previousChats) =>
          previousChats.map((chat) =>
            chat.id === activeChatId
              ? {
                  ...chat,
                  messages: finalMessages,
                  updatedAt: new Date().toISOString(),
                }
              : chat
          )
        );
      } else {
        const newChat: Chat = {
          id: resolvedSessionId || generateChatId(),
          subject,
          title: generateChatTitle(userQuestion),
          messages: finalMessages,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };

        setChats((previousChats) => [newChat, ...previousChats]);
        setActiveChatId(newChat.id);
      }
    } catch (error) {
      console.error("Error communicating with backend:", error);

      const errorMessage: Message = {
        role: "assistant",
        content:
          error instanceof Error
            ? error.message
            : "Sorry, I could not connect to the gateway orchestrator.",
      };

      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // ===================================================
  // Handle Enter Key
  // ===================================================

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ): void => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      sendMessage();
    }
  };

  // ===================================================
  // Handle Default Question
  // ===================================================

  const handleDefaultQuestion = (
    selectedQuestion: string
  ): void => {
    if (
      uploading ||
      loading
    ) {
      return;
    }

    setQuestion(
      selectedQuestion
    );
  };

  // ===================================================
  // Render
  // ===================================================

  return (
    <main className="flex h-screen overflow-hidden bg-slate-950 text-white">

      {/* =================================================
          SIDEBAR
      ================================================= */}

      <ChatSidebar
        chats={chats}
        currentSubject={subject}
        activeChatId={activeChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onBack={onBack}
      />

      {/* =================================================
          MAIN CHAT AREA
      ================================================= */}

      <section className="flex min-w-0 flex-1 flex-col">

        {/* =================================================
            HEADER
        ================================================= */}

        <header className="flex h-16 items-center justify-between border-b border-slate-800 px-6">

          <div>
            <h1 className="font-semibold">
              Educational AI Tutor
            </h1>

            <p className="text-xs text-slate-500">
              Ask questions from your study material
            </p>
          </div>

          {/* =================================================
              SUBJECT
          ================================================= */}

          <div className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white">
            {subjectName}
          </div>

        </header>

        {/* =================================================
            DOCUMENT STATUS
        ================================================= */}

        {documentUploaded &&
          uploadedFile && (
            <div className="border-b border-slate-800 bg-slate-900/70 px-6 py-3">

              <div className="mx-auto flex max-w-4xl items-center justify-between gap-4">

                <div className="flex min-w-0 items-center gap-3">

                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-800">
                    📄
                  </div>

                  <div className="min-w-0">

                    <p className="text-xs font-medium text-slate-400">
                      Uploaded Document
                    </p>

                    <p className="truncate text-sm text-white">
                      {uploadedFile.name}
                    </p>

                  </div>

                </div>

                <div className="flex shrink-0 items-center gap-3">

                  <span className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1 text-xs text-slate-300">
                    Document Mode
                  </span>

                  <button
                    type="button"
                    onClick={
                      handleRemoveDocument
                    }
                    disabled={
                      uploading ||
                      loading
                    }
                    className="rounded-lg px-3 py-1.5 text-xs text-slate-400 transition hover:bg-slate-800 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    Remove
                  </button>

                </div>

              </div>

            </div>
          )}

        {/* =================================================
            UPLOAD ERROR
        ================================================= */}

        {uploadError && (
          <div className="border-b border-red-900/40 bg-red-950/30 px-6 py-3">

            <div className="mx-auto max-w-4xl">

              <p className="text-sm text-red-400">
                {uploadError}
              </p>

            </div>

          </div>
        )}

        {/* =================================================
            MESSAGES
        ================================================= */}

        <div className="flex-1 overflow-y-auto">

          {messages.length === 0 ? (

            // =================================================
            // EMPTY STATE
            // =================================================

            <div className="flex h-full items-center justify-center px-6">

              <div className="max-w-2xl text-center">

                <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-800 text-2xl">
                  {documentUploaded
                    ? "📄"
                    : "💬"}
                </div>

                <h2 className="text-2xl font-semibold">

                  {documentUploaded
                    ? "Ask about your document"
                    : "What would you like to learn?"}

                </h2>

                <p className="mt-3 text-slate-500">

                  {documentUploaded
                    ? `Ask a question about ${uploadedFile?.name}. Answers will be generated from the uploaded document.`
                    : `Ask a question about ${subjectName}.`}

                </p>

                {/* =================================================
                    DEFAULT QUESTIONS
                ================================================= */}

                {!documentUploaded &&
                  defaultQuestions.length >
                    0 && (

                    <div className="mt-6 flex flex-wrap justify-center gap-2">

                      {defaultQuestions.map(
                        (
                          defaultQuestion,
                          index
                        ) => (

                          <button
                            key={index}
                            onClick={() =>
                              handleDefaultQuestion(
                                defaultQuestion
                              )
                            }
                            disabled={
                              uploading ||
                              loading
                            }
                            className="rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-400 transition hover:bg-slate-800 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                          >
                            {defaultQuestion}
                          </button>

                        )
                      )}

                    </div>
                  )}

                {/* =================================================
                    UPLOAD BUTTON
                ================================================= */}

                {!documentUploaded && (
                  <button
                    type="button"
                    onClick={
                      handleOpenFilePicker
                    }
                    disabled={
                      uploading ||
                      loading
                    }
                    className="mt-7 rounded-xl border border-slate-700 bg-slate-900 px-5 py-3 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:bg-slate-800 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    📎 Upload Document
                  </button>
                )}

                {/* =================================================
                    UPLOADING STATUS
                ================================================= */}

                {uploading && (
                  <p className="mt-3 text-xs text-slate-500">
                    Uploading and processing document...
                  </p>
                )}

              </div>

            </div>

          ) : (

            // =================================================
            // CHAT MESSAGES
            // =================================================

            <div className="mx-auto max-w-4xl space-y-8 px-6 py-8">

              {messages.map(
                (
                  message,
                  index
                ) => (

                  <ChatMessage
                    key={index}
                    message={message}
                  />

                )
              )}

              {/* =================================================
                  LOADING
              ================================================= */}

              {loading && (
                <div className="text-sm text-slate-500">
                  {documentUploaded
                    ? "Reading your document..."
                    : "Thinking..."}
                </div>
              )}

            </div>
          )}

        </div>

        {/* =================================================
            INPUT
        ================================================= */}

        <div className="border-t border-slate-800 p-4">

          <div className="mx-auto max-w-4xl">

            {/* =================================================
                UPLOAD BUTTON + DOCUMENT INDICATOR
            ================================================= */}

            <div className="mb-2 flex items-center justify-between">

              <div>

                {!documentUploaded ? (

                  <button
                    type="button"
                    onClick={
                      handleOpenFilePicker
                    }
                    disabled={
                      uploading ||
                      loading
                    }
                    className="rounded-lg px-3 py-1.5 text-xs text-slate-500 transition hover:bg-slate-900 hover:text-slate-300 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    📎 Upload Document
                  </button>

                ) : (

                  <span className="text-xs text-slate-500">
                    📄 Answers are based only on the uploaded document
                  </span>

                )}

              </div>

              {uploading && (
                <span className="text-xs text-slate-500">
                  Uploading...
                </span>
              )}

            </div>

            {/* =================================================
                HIDDEN FILE INPUT
            ================================================= */}

            <input
              ref={fileInputRef}
              type="file"

              /*
               * Content Processing Agent supports:
               *
               * Documents:
               * PDF, DOCX, PPTX, TXT, MD
               *
               * Images:
               * PNG, JPG, JPEG, BMP, TIFF
               *
               * Audio:
               * WAV, MP3, M4A
               *
               * DOC/PPT are included as well because
               * browsers may expose them depending on
               * the installed application/file source.
               */

              accept="
                .pdf,
                .doc,
                .docx,
                .ppt,
                .pptx,
                .txt,
                .md,
                .png,
                .jpg,
                .jpeg,
                .bmp,
                .tiff,
                .wav,
                .mp3,
                .m4a
              "

              onChange={
                handleFileUpload
              }

              className="hidden"
            />

            {/* =================================================
                TEXT INPUT
            ================================================= */}

            <div className="flex items-end gap-3 rounded-2xl border border-slate-700 bg-slate-900 p-2">

              <button
                type="button"
                onClick={isRecording ? stopRecording : startRecording}
                disabled={loading || uploading}
                className={`rounded-xl px-3 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-40 ${
                  isRecording 
                    ? "bg-rose-600 text-white animate-pulse" 
                    : "bg-slate-800 text-slate-350 hover:bg-slate-700 hover:text-white"
                }`}
              >
                {isRecording ? "🛑 Stop" : "🎙️ Voice"}
              </button>

              <textarea
                value={question}

                onChange={(event) =>
                  setQuestion(
                    event.target.value
                  )
                }

                onKeyDown={
                  handleKeyDown
                }

                placeholder={
                  documentUploaded
                    ? "Ask a question about the uploaded document..."
                    : `Ask a question about ${subjectName}...`
                }

                rows={1}

                disabled={
                  uploading
                }

                className="max-h-32 min-h-12 flex-1 resize-none bg-transparent px-3 py-3 text-sm text-white outline-none placeholder:text-slate-600 disabled:cursor-not-allowed disabled:opacity-50"
              />

              <button
                type="button"
                onClick={
                  sendMessage
                }
                disabled={
                  !question.trim() ||
                  loading ||
                  uploading
                }
                className="rounded-xl bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-40"
              >
                ↑
              </button>

            </div>

            <p className="mt-2 text-center text-xs text-slate-600">
              Press Enter to send · Shift + Enter for a new line
            </p>

          </div>

        </div>

      </section>

    </main>
  );
}
