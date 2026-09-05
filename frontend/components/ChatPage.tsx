"use client";

import { useEffect, useRef, useState } from "react";
import ChatSidebar from "@/components/ChatSidebar";
import ChatMessage from "@/components/ChatMessage";
import DocumentsModal, { UploadedDocument } from "@/components/DocumentsModal";

// =====================================================
// Types
// =====================================================

interface ComparisonTableData {
  columns: string[];
  rows: string[][];
}

export interface ChatResponse {
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
  id?: string;
  role: "user" | "assistant";
  content?: string;
  code?: string;
  comparison_table?: ComparisonTableData;
  audio_url?: string;
  topic?: string;
  intent?: string;
  difficulty?: string;
  unit?: string;
  subject?: string;
  is_voice_response?: boolean;
  image_url?: string | null;
  generated_image?: string;
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
  onBack: () => void;
  onAuthFailure?: () => void;
  onRequireAuth?: (message?: string) => void;
  onOpenQuiz: (props: QuizFlashcardInitProps) => void;
  onOpenFlashcards: (props: QuizFlashcardInitProps) => void;
}

interface QuizFlashcardInitProps {
  launchOrigin?: "home" | "chat";
  initialSubject?: string;
  initialTopic?: string;
  initialDifficulty?: string;
  initialDocumentUploaded?: boolean;
  initialNumQuestions?: number;
  initialNumCards?: number;
  autoStart?: boolean;
}

// =====================================================
// Storage Keys
// =====================================================

const STORAGE_KEY =
  "educational-content-generator-chats";

// =====================================================
// Backend URLs
// =====================================================

const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const PROCESS_CONTENT_URL =
  `${BACKEND_URL}/process-content`;

const UPLOAD_URL =
  `${BACKEND_URL}/upload/`;

const MULTIMEDIA_URL =
  process.env.NEXT_PUBLIC_MULTIMEDIA_URL || "http://127.0.0.1:8003";

// =====================================================
// Subject Names
// =====================================================

const SUBJECT_ALIASES = [
  ["operating system", "OS"], ["dbms", "DBMS"],
  ["object oriented programming", "OOP"], ["oop", "OOP"],
  ["cryptography", "CNS"], ["data structure", "DATA STRUCTURE"],
  ["software engineering", "SE"], ["artificial intelligence", "AI"],
].map(([name, code]) => [name, code] as const);

function parseGenerationRequest(query: string): { type: "quiz" | "flashcards"; subject?: string; topic?: string } | null {
  const normalizedQuery = query.trim();
  const match = normalizedQuery.match(/^(?:please\s+)?(?:generate|make|create|prepare)\s+(?:me\s+)?(?:a\s+)?(?:\d+\s+)?(quiz|mcqs?|questions?|flashcards?)\b(?:\s+(?:on|about|for|covering)\s+(.+))?$/i)
    || normalizedQuery.match(/^(?:please\s+)?(?:quiz|flashcards?)\s+me\s+on\s+(.+)$/i);
  if (!match) return null;
  const isFlashcards = /flashcards?/i.test(match[1]) || /^(?:please\s+)?flashcards?\s+me\s+on/i.test(normalizedQuery);
  const isDirectQuiz = /^(?:please\s+)?quiz\s+me\s+on/i.test(normalizedQuery);
  const scope = (isDirectQuiz || (isFlashcards && match.length === 2) ? match[1] : match[2])?.trim().replace(/[?.!]+$/, "");
  let subject: string | undefined;
  let topic = scope;
  if (scope) {
    const alias = SUBJECT_ALIASES.sort(([first], [second]) => second.length - first.length)
      .find(([name]) => scope.toLowerCase() === name || scope.toLowerCase().startsWith(`${name} `));
    if (alias) {
      subject = alias[1];
      topic = scope.slice(alias[0].length).trim();
    }
  }
  return { type: isFlashcards ? "flashcards" : "quiz", subject, topic: topic || undefined };
}

function generateMessageId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function ensureMessageIds(messages: Message[]): Message[] {
  return messages.map((message) => ({ ...message, id: message.id || generateMessageId() }));
}

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
  onBack,
  onAuthFailure,
  onRequireAuth,
  onOpenQuiz,
  onOpenFlashcards,
}: ChatPageProps) {
  // ===================================================
  // Guest Trial State
  // ===================================================

  const [isLoggedIn, setIsLoggedIn] =
    useState<boolean>(false);

  const [guestChatCount, setGuestChatCount] =
    useState<number>(0);

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    setIsLoggedIn(!!token);
    const count = parseInt(localStorage.getItem("guest_chat_count") || "0", 10);
    setGuestChatCount(count);
  }, []);

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
  // Uploaded Document & Persistent Study Materials
  // ===================================================

  const [uploadedFile, setUploadedFile] =
    useState<File | null>(null);

  const [uploadedDocName, setUploadedDocName] =
    useState<string>("");

  const [subjectDocuments, setSubjectDocuments] =
    useState<Array<{ id?: number | string; filename?: string; original_name?: string; subject?: string }>>([]);

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

  // Voice Recording state
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

  // Documents Library state
  const [isDocumentsModalOpen, setIsDocumentsModalOpen] = useState<boolean>(false);
  const [totalDocumentCount, setTotalDocumentCount] = useState<number>(0);

  // ===================================================
  // Load Saved Chats & Documents from Database
  // ===================================================

  const fetchSubjectDocuments = async () => {
    const token = localStorage.getItem("authToken");
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;
    try {
      const res = await fetch(`${BACKEND_URL}/upload/documents`, { headers });
      if (res.ok) {
        const docs = await res.json();
        setSubjectDocuments(docs);
        if (Array.isArray(docs)) {
          setTotalDocumentCount(docs.length);
        }
      }
    } catch (err) {
      console.warn("Backend documents service not reached, using local state:", err);
    }
  };

  const handleSelectExistingDocument = (doc: UploadedDocument) => {
    setUploadedDocName(doc.filename);
    setUploadedFile(null);
    setDocumentUploaded(true);
    setUploadError("");

    fetchSubjectDocuments();
  };

  useEffect(() => {
    const fetchChats = async () => {
      const token = localStorage.getItem("authToken");
      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;

      try {
        const response = await fetch(`${BACKEND_URL}/chats`, { headers });
        if (response.status === 401 && onAuthFailure) {
          onAuthFailure();
          return;
        }
        if (response.ok) {
          const backendChats = await response.json();
          if (Array.isArray(backendChats) && backendChats.length > 0) {
            setChats(backendChats.map((chat: Chat) => ({ ...chat, messages: ensureMessageIds(chat.messages) })));
            return;
          }
        }
      } catch (err) {
        console.warn("Backend chats service not reached, falling back to local storage:", err);
      }

      try {
        const savedChats = localStorage.getItem(STORAGE_KEY);
        if (savedChats) {
          const parsedChats = JSON.parse(savedChats);
          if (Array.isArray(parsedChats)) {
            setChats((parsedChats as Chat[]).map((chat) => ({ ...chat, messages: ensureMessageIds(chat.messages) })));
          }
        }
      } catch (error) {
        console.error("Could not load saved chats:", error);
      }
    };

    fetchChats();
    fetchSubjectDocuments();
  }, []);

  const handleDeleteChat = async (chatId: string) => {
    const token = localStorage.getItem("authToken");
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;
    try {
      await fetch(`${BACKEND_URL}/chats/${chatId}`, {
        method: "DELETE",
        headers,
      });
    } catch (err) {
      console.error("Failed to delete chat on backend:", err);
    }
    setChats((prev) => prev.filter((c) => c.id !== chatId));
    if (activeChatId === chatId) {
      handleNewChat();
    }
  };


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
  // Create New Chat
  // ===================================================

  const handleNewChat = (): void => {
    setMessages([]);
    setQuestion("");
    setActiveChatId(null);
  };

  const handleGenerateQuiz = (
    subj: string,
    topic?: string,
    difficulty?: string,
    docUploaded?: boolean,
  ): void => {
      onOpenQuiz({
        launchOrigin: "chat",
      initialSubject: subj,
      initialTopic: topic,
      initialDifficulty: difficulty,
      initialDocumentUploaded: docUploaded,
      initialNumQuestions: 5,
      autoStart: true,
    });
  };

  const handleGenerateFlashcards = (
    subj: string,
    topic?: string,
    difficulty?: string,
    docUploaded?: boolean,
  ): void => {
      onOpenFlashcards({
        launchOrigin: "chat",
      initialSubject: subj,
      initialTopic: topic,
      initialDifficulty: difficulty,
      initialDocumentUploaded: docUploaded,
      initialNumCards: 5,
      autoStart: true,
    });
  };

  const handleGenerateVoice = async (text: string): Promise<string> => {
    const response = await fetch(`${MULTIMEDIA_URL}/multimedia/tts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) throw new Error(`TTS request failed: ${response.status}`);
    const data = await response.json();
    if (data.audio_url) return data.audio_url;
    if (data.audio_path) {
      const filename = data.audio_path.split(/[\\/]/).pop();
      if (filename) return `${MULTIMEDIA_URL}/outputs/audio/${filename}`;
    }
    throw new Error("TTS response did not include an audio URL.");
  };

  const handleGenerateImage = async (
    prompt: string,
    subj: string,
    targetMessageId?: string,
  ): Promise<string> => {
    const response = await fetch(`${MULTIMEDIA_URL}/multimedia/image`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    if (!response.ok) throw new Error("Image generation failed. Please try again.");
    const data = await response.json();
    const imagePath = data.image_url || data.image_path;
    if (!imagePath) throw new Error("Image generation returned no image.");
    const imageUrl = imagePath.startsWith("http")
      ? imagePath
      : `${MULTIMEDIA_URL}/outputs/images/${imagePath.split(/[\\/]/).pop()}`;
    setMessages((previous) => previous.map((message) => (
      message.id === targetMessageId
        ? { ...message, image_url: imageUrl, generated_image: imageUrl }
        : message
    )));
    return imageUrl;
  };

  // ===================================================
  // Select Existing Chat
  // ===================================================

  const handleSelectChat = (
    chat: Chat
  ): void => {
    setActiveChatId(chat.id);
    setMessages(ensureMessageIds(chat.messages));
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

      formData.append(
        "file",
        file
      );

      console.log(
        "Uploading file:",
        file.name
      );

      // =================================================
      // Send File To Backend with Auth Token
      // =================================================

      const token = localStorage.getItem("authToken");
      const uploadHeaders: Record<string, string> = {};
      if (token) {
        uploadHeaders["Authorization"] = `Bearer ${token}`;
      }

      const response =
        await fetch(
          UPLOAD_URL,
          {
            method: "POST",
            headers: uploadHeaders,
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
      setUploadedDocName(file.name);
      setDocumentUploaded(true);
      setUploadError("");
      fetchSubjectDocuments();

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
      setUploadedDocName("");

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
    setUploadedDocName("");
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
    const token = localStorage.getItem("authToken");
    if (!token) {
      const currentCount = parseInt(localStorage.getItem("guest_chat_count") || "0", 10);
      if (currentCount >= 10) {
        if (onRequireAuth) {
          onRequireAuth("You have asked 10 free questions. Sign in or create an account to unlock unlimited chat questions, quizzes, and flashcards!");
        } else {
          alert("Free trial limit reached: You have asked 10 questions. Please sign in or create an account for unlimited access.");
        }
        return;
      }
    }

    setLoading(true);

    const tempUserMsg: Message = {
      role: "user",
      content: "🎤 [Voice Message sending...]",
    };

    const updatedMessages = [...messages, tempUserMsg];
    setMessages(updatedMessages);

    try {
      const headers: Record<string, string> = {};
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const formData = new FormData();
      formData.append("file", audioBlob, "recording.wav");
      if (activeChatId) {
        formData.append("session_id", activeChatId);
      }
      formData.append("document_uploaded", String(documentUploaded));
      if (documentUploaded && uploadedDocName) {
        formData.append("document_name", uploadedDocName);
      }

      const response = await fetch(`${BACKEND_URL}/voice/qa`, {
        method: "POST",
        headers,
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Voice Q&A Error: ${response.status}`);
      }

      const data = await response.json();

      if (!token) {
        const newCount = (parseInt(localStorage.getItem("guest_chat_count") || "0", 10)) + 1;
        localStorage.setItem("guest_chat_count", String(newCount));
        setGuestChatCount(newCount);
      }

      const finalUserMsg: Message = {
        id: generateMessageId(),
        role: "user",
        content: `🎤 ${data.transcript}`,
      };

      const assistantMsg: Message = {
        id: generateMessageId(),
        role: "assistant",
        content: data.answer,
        audio_url: data.audio_url,
        comparison_table: data.comparison_table,
        code: data.code,
        topic: data.topic,
        difficulty: data.difficulty,
        subject: data.subject,
        intent: data.intent,
        is_voice_response: Boolean(data.audio_url),
      };

      const finalMessages = [...messages, finalUserMsg, assistantMsg];
      setMessages(finalMessages);

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
          subject: data.subject || "GENERAL",
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

    const token = localStorage.getItem("authToken");
    if (!token) {
      const currentCount = parseInt(localStorage.getItem("guest_chat_count") || "0", 10);
      if (currentCount >= 10) {
        if (onRequireAuth) {
          onRequireAuth("You have asked 10 free questions. Sign in or create an account to unlock unlimited chat questions, quizzes, and flashcards!");
        } else {
          alert("Free trial limit reached: You have asked 10 questions. Please sign in or create an account for unlimited access.");
        }
        return;
      }
    }

    const userQuestion = question.trim();

    const generationRequest = parseGenerationRequest(userQuestion);
    if (generationRequest) {
      const launchProps: QuizFlashcardInitProps = {
        launchOrigin: "chat",
        initialSubject: generationRequest.subject,
        initialTopic: generationRequest.topic,
        initialNumQuestions: 5,
        initialNumCards: 5,
        autoStart: true,
      };
      if (generationRequest.type === "quiz") {
        onOpenQuiz(launchProps);
      } else {
        onOpenFlashcards(launchProps);
      }
      setQuestion("");
      return;
    }

    setQuestion("");

    const userMessage: Message = {
      id: generateMessageId(),
      role: "user",
      content: userQuestion,
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setLoading(true);

    try {
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
          question: userQuestion,
          document_uploaded: documentUploaded,
          document_name: documentUploaded ? uploadedDocName : undefined,
          filename: documentUploaded ? uploadedDocName : undefined,
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

      if (!token) {
        const newCount = (parseInt(localStorage.getItem("guest_chat_count") || "0", 10)) + 1;
        localStorage.setItem("guest_chat_count", String(newCount));
        setGuestChatCount(newCount);
      }

      const assistantMessage: Message = {
        id: generateMessageId(),
        role: "assistant",
        content: data.answer || data.summary || "I could not generate an answer.",
        code: data.code,
        comparison_table: data.comparison_table,
        audio_url: data.audio_url,
        topic: data.topic,
        intent: data.intent,
        difficulty: data.difficulty,
        unit: data.unit,
        subject: data.subject,
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);

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
          subject: data.subject || "GENERAL",
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
    <main className="flex h-screen overflow-hidden bg-[#F8FAFC] text-slate-800 font-sans">

      {/* =================================================
          SIDEBAR
      ================================================= */}

      <ChatSidebar
        chats={chats}
        activeChatId={activeChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
        onBack={onBack}
        onOpenDocuments={() => setIsDocumentsModalOpen(true)}
        documentCount={totalDocumentCount || subjectDocuments.length}
        activeDocumentName={documentUploaded ? (uploadedFile?.name || uploadedDocName) : ""}
        onUnloadDocument={handleRemoveDocument}
      />

      {/* =================================================
          MAIN CHAT AREA
      ================================================= */}

      <section className="flex min-w-0 flex-1 flex-col">

        {/* =================================================
            HEADER
        ================================================= */}

        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6 shadow-xs">

          <div>
            <h1 className="font-serif text-lg font-semibold tracking-wide text-slate-900">
              Educational AI Academic Tutor
            </h1>

            <p className="text-xs text-[#C59B27] font-medium">
              Ask questions & synthesize knowledge from your course materials
            </p>
          </div>

        </header>

        {/* =================================================
            DOCUMENT STATUS
        ================================================= */}

        {documentUploaded && (uploadedFile || uploadedDocName) && (
          <div className="border-b border-[#C59B27]/25 bg-amber-50/75 px-6 py-3 shadow-2xs">

            <div className="mx-auto flex max-w-4xl items-center justify-between gap-4">

              <div className="flex min-w-0 items-center gap-3">

                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-[#C59B27]/30 bg-white text-[#C59B27] shadow-xs">
                  📄
                </div>

                <div className="min-w-0">

                  <p className="text-xs font-semibold uppercase tracking-wider text-[#C59B27]">
                    Active Study Document {subjectDocuments.length > 1 ? `(${subjectDocuments.length} in DB)` : ""}
                  </p>

                  <p className="truncate text-sm text-slate-900 font-medium">
                    {uploadedFile?.name || uploadedDocName}
                  </p>

                </div>

              </div>

              <div className="flex shrink-0 items-center gap-2.5">

                <span className="rounded-full border border-[#C59B27]/40 bg-amber-100 px-3 py-1 text-xs font-medium text-[#9A7318]">
                  Document Mode (Saved)
                </span>

                <button
                  type="button"
                  onClick={() => setIsDocumentsModalOpen(true)}
                  className="rounded-lg border border-[#C59B27]/40 bg-white px-2.5 py-1 text-xs font-semibold text-[#9A7318] transition hover:bg-[#C59B27] hover:text-white shadow-2xs"
                  title="Switch to another previously uploaded document"
                >
                  Switch Doc
                </button>

                <button
                  type="button"
                  onClick={handleRemoveDocument}
                  disabled={uploading || loading}
                  className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 transition hover:bg-slate-50 hover:text-rose-600 disabled:cursor-not-allowed disabled:opacity-40 shadow-2xs"
                >
                  Unload
                </button>

              </div>

            </div>

          </div>
        )}


        {/* =================================================
            UPLOAD ERROR
        ================================================= */}

        {uploadError && (
          <div className="border-b border-red-200 bg-red-50 px-6 py-3">

            <div className="mx-auto max-w-4xl">

              <p className="text-sm text-red-600 font-medium">
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

                <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl border border-[#C59B27]/40 bg-white text-2xl text-[#C59B27] shadow-md">
                  {documentUploaded
                    ? "📄"
                    : "💬"}
                </div>

                <h2 className="font-serif text-3xl font-medium tracking-tight text-slate-900">

                  {documentUploaded
                    ? "Ask about your document"
                    : "What would you like to master today?"}

                </h2>

                <p className="mt-3 text-slate-600">

                  {documentUploaded
                    ? `Ask a question about ${uploadedFile?.name}. Answers will be generated directly from the uploaded text.`
                    : "Ask a question about any academic subject, concept, or algorithm."}

                </p>

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
                    className="mt-7 rounded-xl border border-[#C59B27]/50 bg-white px-6 py-3 text-sm font-semibold text-[#C59B27] shadow-sm transition hover:border-[#C59B27] hover:bg-[#C59B27] hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    📎 Upload Course Document
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
                    key={message.id || index}
                    message={message}
                    currentSubject={message.subject || ""}
                    onGenerateQuiz={handleGenerateQuiz}
                    onGenerateFlashcards={handleGenerateFlashcards}
                    onGenerateVoice={handleGenerateVoice}
                    onGenerateImage={handleGenerateImage}
                    documentUploaded={documentUploaded}
                  />

                )
              )}

              {/* =================================================
                  LOADING
              ================================================= */}

              {loading && (
                <div className="text-sm text-slate-500 font-medium">
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

        <div className="border-t border-slate-200 bg-white p-4 shadow-sm">

          <div className="mx-auto max-w-4xl">

            {/* =================================================
                HIDDEN FILE INPUT
            ================================================= */}

            <input
              ref={fileInputRef}
              type="file"
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

            {!isLoggedIn && (
              <div className="mb-2.5 flex items-center justify-between rounded-xl border border-[#C59B27]/30 bg-amber-50/80 px-4 py-2 text-xs text-[#9A7318]">
                <span>Free Trial: <b>{guestChatCount} of 10</b> questions asked</span>
                {onRequireAuth && (
                  <button
                    type="button"
                    onClick={() => onRequireAuth("Sign up or log in to unlock unlimited chat questions, quizzes, and flashcards!")}
                    className="font-semibold text-[#C59B27] underline hover:text-slate-900 transition"
                  >
                    Sign In for Unlimited →
                  </button>
                )}
              </div>
            )}

            <div className="flex items-end gap-3 rounded-2xl border border-slate-300 bg-slate-50 p-2 focus-within:border-[#C59B27] focus-within:bg-white focus-within:ring-1 focus-within:ring-[#C59B27]/30 shadow-xs transition">

              {!documentUploaded ? (
                <button
                  type="button"
                  onClick={handleOpenFilePicker}
                  disabled={uploading || loading}
                  className="shrink-0 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-500 transition hover:bg-slate-100 hover:text-[#C59B27] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  📎 Upload
                </button>
              ) : (
                <span
                  className="shrink-0 px-3 py-2.5 text-sm text-[#C59B27]"
                  title="Answers are based only on the uploaded document"
                >
                  📄
                </span>
              )}

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
                    : "Ask anything you want to learn..."
                }

                rows={1}

                disabled={
                  uploading
                }

                className="max-h-32 min-h-12 min-w-0 flex-1 resize-none bg-transparent px-3 py-3 text-sm text-slate-900 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed disabled:opacity-50"
              />

              <button
                type="button"
                onClick={isRecording ? stopRecording : startRecording}
                disabled={loading || uploading}
                className={`shrink-0 rounded-xl px-3 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-40 ${
                  isRecording
                    ? "bg-rose-600 text-white animate-pulse"
                    : "border border-slate-200 bg-slate-100 text-slate-700 hover:border-[#C59B27]/40 hover:bg-slate-200 hover:text-slate-900"
                }`}
              >
                {isRecording ? "🛑 Stop" : "🎙️ Voice"}
              </button>

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
                className="shrink-0 rounded-xl bg-[#C59B27] px-4 py-3 text-sm font-bold text-white transition hover:bg-[#B38A1F] disabled:cursor-not-allowed disabled:opacity-40 shadow-sm"
              >
                ↑
              </button>

            </div>

            <p className="mt-2 text-center text-xs text-slate-400">
              Press Enter to send · Shift + Enter for a new line
            </p>

          </div>

        </div>

      </section>

      <DocumentsModal
        isOpen={isDocumentsModalOpen}
        onClose={() => setIsDocumentsModalOpen(false)}
        activeDocumentName={documentUploaded ? (uploadedFile?.name || uploadedDocName) : ""}
        onSelectDocument={handleSelectExistingDocument}
        onUnloadDocument={handleRemoveDocument}
      />

    </main>
  );
}
