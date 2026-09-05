"use client";

import { useEffect, useRef, useState } from "react";
import ComparisonTable from "./ComparisonTable";

interface ComparisonTableData {
  columns: string[];
  rows: string[][];
}

interface ChatMessageData {
  id?: string;
  role: "user" | "assistant";
  content?: string;
  code?: string;
  comparison_table?: ComparisonTableData;
  audio_url?: string;
  topic?: string;
  difficulty?: string;
  unit?: string;
  subject?: string;
  intent?: string;
  image_url?: string | null;
  generated_image?: string;
  is_voice_response?: boolean;
}

interface ChatMessageProps {
  message: ChatMessageData;
  currentSubject?: string;
  onGenerateQuiz?: (subject: string, topic?: string, difficulty?: string, documentUploaded?: boolean) => void;
  onGenerateFlashcards?: (subject: string, topic?: string, difficulty?: string, documentUploaded?: boolean) => void;
  onGenerateVoice?: (text: string) => void | Promise<string>;
  onGenerateImage?: (prompt: string, subject: string, messageId?: string) => void | Promise<string>;
  documentUploaded?: boolean;
}

let activePlayback: { stop: () => void } | null = null;

export default function ChatMessage({
  message,
  currentSubject = "",
  onGenerateQuiz = () => undefined,
  onGenerateFlashcards = () => undefined,
  onGenerateVoice = () => undefined,
  onGenerateImage = () => undefined,
  documentUploaded = false,
}: ChatMessageProps) {
  const isUser = message.role === "user";
  const [voiceState, setVoiceState] = useState<"idle" | "playing" | "paused">("idle");
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const cleanupAudioRef = useRef<(() => void) | null>(null);
  const [imageGenerating, setImageGenerating] = useState(false);
  const [imageError, setImageError] = useState<string | null>(null);

  const stopAudio = (resetPosition = true) => {
    cleanupAudioRef.current?.();
    cleanupAudioRef.current = null;
    if (audioRef.current) {
      audioRef.current.pause();
      if (resetPosition) audioRef.current.currentTime = 0;
    }
    audioRef.current = null;
    setVoiceState("idle");
    if (activePlayback?.stop === stopAudio) activePlayback = null;
  };

  const startAudioPlayback = (audioUrl: string) => {
    activePlayback?.stop();
    const audio = new Audio(audioUrl);
    audioRef.current = audio;

    const handlePlay = () => setVoiceState("playing");
    const handlePause = () => setVoiceState("paused");
    const handleEnded = () => stopAudio(false);
    const handleError = () => {
      setVoiceError("Unable to play this audio.");
      stopAudio();
    };
    const handleVisibilityChange = () => {
      if (document.visibilityState === "hidden" && !audio.paused) audio.pause();
    };

    audio.addEventListener("play", handlePlay);
    audio.addEventListener("pause", handlePause);
    audio.addEventListener("ended", handleEnded);
    audio.addEventListener("error", handleError);
    document.addEventListener("visibilitychange", handleVisibilityChange);
    cleanupAudioRef.current = () => {
      audio.removeEventListener("play", handlePlay);
      audio.removeEventListener("pause", handlePause);
      audio.removeEventListener("ended", handleEnded);
      audio.removeEventListener("error", handleError);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
    activePlayback = { stop: stopAudio };
    audio.play().catch(() => {
      setVoiceError("Unable to play this audio.");
      stopAudio();
    });
  };

  useEffect(() => {
    if (!isUser && message.is_voice_response && message.audio_url) {
      startAudioPlayback(message.audio_url);
    }
    return () => stopAudio();
  }, [message.id, message.is_voice_response, message.audio_url]);

  const handleGenerateVoice = () => {
    if (isUser || !message.content) return;
    setVoiceError(null);
    if (voiceState === "playing") {
      audioRef.current?.pause();
      return;
    }
    if (voiceState === "paused") {
      audioRef.current?.play().catch(() => {
        setVoiceError("Unable to play this audio.");
        stopAudio();
      });
      return;
    }
    if (message.audio_url) {
      startAudioPlayback(message.audio_url);
      return;
    }
    Promise.resolve(onGenerateVoice(message.content))
      .then((audioUrl) => {
        if (!audioUrl) throw new Error("No audio URL was returned.");
        startAudioPlayback(audioUrl);
      })
      .catch((err: unknown) => {
        setVoiceError(err instanceof Error ? err.message : "Unable to generate audio.");
      });
  };

  const handleGenerateImage = () => {
    if (isUser || !message.content) return;
    setImageGenerating(true);
    setImageError(null);
    const prompt = `Educational diagram explaining: ${message.content.substring(0, 200)}. Clean, labeled, textbook style.`;
    Promise.resolve(onGenerateImage(prompt, currentSubject, message.id))
      .catch((err: unknown) => {
        setImageError(err instanceof Error ? err.message : "Image generation failed.");
      })
      .finally(() => setImageGenerating(false));
  };

  const handleDownloadImage = async (imageUrl: string) => {
    try {
      const response = await fetch(imageUrl);
      if (!response.ok) throw new Error();
      const blobUrl = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = "educational-image.png";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(blobUrl);
    } catch {
      setImageError("Unable to download the generated image.");
    }
  };

  const handleGenerateQuiz = () => {
    if (!isUser) {
      const messageSubject = message.subject?.trim() || currentSubject.trim();
      onGenerateQuiz(
        messageSubject.toUpperCase() === "UNKNOWN" ? "" : messageSubject,
        message.topic,
        message.difficulty,
        documentUploaded,
      );
    }
  };

  const handleGenerateFlashcards = () => {
    if (!isUser) onGenerateFlashcards(currentSubject, message.topic, message.difficulty, documentUploaded);
  };

  const generatedImage = message.image_url || message.generated_image;

  return (
    <div
      className={`flex w-full ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`max-w-3xl rounded-2xl px-5 py-4 transition shadow-md ${
          isUser
            ? "bg-[#C59B27] text-white font-medium border border-[#B38A1F]"
            : "bg-white text-slate-800 border border-slate-200/80"
        }`}
      >
        {/* Message text */}
        {message.content && (
          <div className="whitespace-pre-wrap leading-7">
            {message.content}
          </div>
        )}

        {!isUser && generatedImage && (
          <div className="mt-4 overflow-hidden rounded-xl border border-slate-200 bg-slate-50 shadow-2xs">
            <div className="border-b border-slate-200 bg-slate-100/70 px-3 py-2 text-xs font-semibold uppercase tracking-wider text-[#C59B27]">Generated Diagram</div>
            <img src={generatedImage} alt="Educational illustration" className="max-h-96 w-full bg-white object-contain p-2" />
            <div className="border-t border-slate-200 bg-slate-50 px-3 py-2">
              <button type="button" onClick={() => handleDownloadImage(generatedImage)} className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-100 hover:text-slate-900 shadow-2xs">
                Download Image
              </button>
            </div>
          </div>
        )}

        {!isUser && imageError && <p className="mt-3 text-sm text-rose-500 font-medium">{imageError}</p>}

        {!isUser && voiceError && <p className="mt-3 text-sm text-rose-500 font-medium">{voiceError}</p>}

        {/* Code */}
        {!isUser && message.code && (
          <div className="mt-4 overflow-hidden rounded-xl border border-slate-300 bg-slate-900 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-800 bg-slate-800 px-4 py-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-[#E5C365]">
                Code Reference
              </span>
            </div>

            <pre className="overflow-x-auto p-4 text-sm leading-6 text-slate-100 font-mono">
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

        {!isUser && message.intent !== "out_of_scope" && (
          <div className="mt-4 flex flex-wrap gap-2 pt-2 border-t border-slate-100">
            <button type="button" onClick={handleGenerateQuiz} disabled={voiceState === "playing" || imageGenerating} className="rounded-lg border border-[#C59B27]/40 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-[#C59B27] transition hover:bg-[#C59B27] hover:text-white disabled:cursor-not-allowed disabled:opacity-50 shadow-2xs" title="Generate a quiz from this topic">
              📝 Quiz
            </button>
            <button type="button" onClick={handleGenerateFlashcards} disabled={voiceState === "playing" || imageGenerating} className="rounded-lg border border-[#C59B27]/40 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-[#C59B27] transition hover:bg-[#C59B27] hover:text-white disabled:cursor-not-allowed disabled:opacity-50 shadow-2xs" title="Generate flashcards from this topic">
              🎴 Flashcards
            </button>
            <button type="button" onClick={handleGenerateVoice} disabled={imageGenerating} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-100 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-50 shadow-2xs" title="Listen to this response">
              {voiceState === "playing" ? "⏸ Playing" : voiceState === "paused" ? "▶️ Paused" : "🔊 Listen"}
            </button>
            <button type="button" onClick={handleGenerateImage} disabled={voiceState === "playing" || imageGenerating} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-100 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-50 shadow-2xs" title="Generate educational diagram">
              {imageGenerating ? "⏳ Generating..." : "🖼️ Image"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
