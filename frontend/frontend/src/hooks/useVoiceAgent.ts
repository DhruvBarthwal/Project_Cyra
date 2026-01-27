import { useRef, useState } from "react";
import { createDeepgramSocket } from "@/lib/deepgram";
import { sendToBackend } from "@/lib/api";
import { speak } from "@/lib/tts";

export function useVoiceAgent( onMessage?: (role: "user" | "agent", text: string) => void) {
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  const [listening, setListening] = useState(false);
  const [lastEmailId, setLastEmailId] = useState<string | null>(null);
  const lastEmailIdRef = useRef<string | null>(null);
  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    socketRef.current = createDeepgramSocket(async (finalText) => {

      onMessage?.("user", finalText);

      setListening(false);

      console.log("PAYLOAD:", {
        text: finalText,
        email_id: lastEmailIdRef.current,
      });

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

      if (data.email_id) {
        setLastEmailId(data.email_id);
      }

      if (typeof data.email_id === "string") {

        lastEmailIdRef.current = data.email_id; 
        setLastEmailId(data.email_id);
      }

      if (data.deleted === true) {
        lastEmailIdRef.current = null;
        setLastEmailId(null);
      }

      onMessage?.("agent", data.response);

      speak(data.response);
    });

    socketRef.current.onopen = () => {
      console.log(" Starting MediaRecorder");

      mediaRecorder.current = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      mediaRecorder.current.ondataavailable = (e) => {
        if (socketRef.current?.readyState === WebSocket.OPEN) {
          socketRef.current.send(e.data);
        }
      };

      mediaRecorder.current.start(250);
      setListening(true);
    };
  }

  function stop() {
    mediaRecorder.current?.stop();
    mediaRecorder.current = null;

    socketRef.current?.close();
    socketRef.current = null;

    setListening(false);
  }

  async function reset() {
    stop();

    lastEmailIdRef.current = null;
    setLastEmailId(null);

    await sendToBackend("reset", null);

    setTimeout(() => start(), 300);
  }

  return { start, stop, reset, listening };
}
