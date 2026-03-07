import { useRef, useState, useCallback } from "react";
import { createDeepgramSocket } from "@/lib/deepgram";
import { sendToBackend } from "@/lib/api";
import { speak } from "@/lib/tts";

function cleanForSpeech(text: string): string {
  return text
    .replace(/\*\*/g, "")    
    .replace(/\*/g, "")         
    .replace(/#{1,6}\s/g, "")    
    .replace(/`/g, "")           
    .replace(/\[([^\]]+)\]\([^\)]+\)/g, "$1")  
    .replace(/\n{3,}/g, "\n\n")  
}

export function useVoiceAgent(onMessage?: (role: "user" | "agent", text: string) => void) {
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const isSpeaking = useRef(false);

  const [listening, setListening] = useState(false);
  const lastEmailIdRef = useRef<string | null>(null);
  const [lastEmailId, setLastEmailId] = useState<string | null>(null);

  function startRecording() {
    if (!streamRef.current || !socketRef.current) return;
    mediaRecorder.current = new MediaRecorder(streamRef.current, {
      mimeType: "audio/webm;codecs=opus",
    });
    mediaRecorder.current.ondataavailable = (e) => {
      if (socketRef.current?.readyState === WebSocket.OPEN && !isSpeaking.current) {
        socketRef.current.send(e.data);
      }
    };
    mediaRecorder.current.start(250);
    setListening(true);
  }

  function startSession() {
    if (!streamRef.current) return;

    socketRef.current = createDeepgramSocket(async (finalText) => {
      if (isSpeaking.current) return;

      mediaRecorder.current?.stop();
      mediaRecorder.current = null;
      setListening(false);

      onMessage?.("user", finalText);

      const lower = finalText.toLowerCase();
      const isComposeFlow =
        lower.includes("create") ||
        lower.includes("compose") ||
        lower.includes("write") ||
        lower.includes("send mail");

      const data = await sendToBackend(
        finalText,
        isComposeFlow || lastEmailIdRef.current == null
          ? null
          : lastEmailIdRef.current
      );

      if (typeof data.email_id === "string") {
        lastEmailIdRef.current = data.email_id;
        setLastEmailId(data.email_id);
      }
      if (data.deleted === true) {
        lastEmailIdRef.current = null;
        setLastEmailId(null);
      }

      onMessage?.("agent", data.response);

      isSpeaking.current = true;
      speak(cleanForSpeech(data.response), () => {
        setTimeout(() => {
          isSpeaking.current = false;

          socketRef.current?.close();
          socketRef.current = null;
          startSession(); 
        }, 200);  
      });

    }, isSpeaking);

    socketRef.current.onopen = () => {
      console.log("Deepgram ready - listening...");
      startRecording();
    };
  }

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef.current = stream;
    startSession();
  }

  function stop() {
    mediaRecorder.current?.stop();
    mediaRecorder.current = null;
    socketRef.current?.close();
    socketRef.current = null;
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;
    setListening(false);
  }

  async function reset() {
    stop();
    lastEmailIdRef.current = null;
    setLastEmailId(null);
    await sendToBackend("reset", null);
    setTimeout(() => start(), 300);
  }

  return { start, stop, reset, listening, lastEmailId };
}