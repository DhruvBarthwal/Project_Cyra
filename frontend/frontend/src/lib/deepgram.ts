export function createDeepgramSocket(
  onFinalTranscript: (text: string) => void,
  isSpeaking: { current: boolean }  // ← no React import, no deprecated type
) {
  const apiKey = process.env.NEXT_PUBLIC_DEEPGRAM_API_KEY;

  if (!apiKey) {
    throw new Error("Deepgram API key missing");
  }

  const socket = new WebSocket(
    "wss://api.deepgram.com/v1/listen" +
      "?model=nova-2" +
      "&language=en-IN" +
      "&punctuate=true" +
      "&interim_results=true" +
      "&utterance_end_ms=1200" +
      "&vad_events=true",
    ["token", apiKey]
  );

  let accumulated = "";

  socket.onopen = () => {
    console.log("Deepgram socket connected");
  };

  socket.onerror = (e) => {
    console.error("Deepgram socket error", e);
  };

  socket.onclose = () => {
    console.log("Deepgram socket closed");
  };

  socket.onmessage = (msg) => {
    const data = JSON.parse(msg.data);

    if (data.type === "UtteranceEnd") {
      if (accumulated.trim() && !isSpeaking.current) {  
        console.log("Full transcript:", accumulated.trim());
        onFinalTranscript(accumulated.trim());
      }
      accumulated = ""; 
      return;
    }

    if (data.type !== "Results") return;

    const transcript = data.channel?.alternatives?.[0]?.transcript;
    if (!transcript) return;

    if (data.is_final && !isSpeaking.current) { 
      accumulated += (accumulated ? " " : "") + transcript;
    }
  };

  return socket;
}