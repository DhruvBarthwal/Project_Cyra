export function createDeepgramSocket(
  onFinalTranscript: (text: string) => void
) {
  const apiKey = process.env.NEXT_PUBLIC_DEEPGRAM_API_KEY;

  if (!apiKey) {
    throw new Error("Deepgram API key missing");
  }

  const socket = new WebSocket(
    "wss://api.deepgram.com/v1/listen" +
      "?model=nova-2" +
      "&language=en-US" +
      "&punctuate=true" +
      "&interim_results=true",
    ["token", apiKey]
  );

  socket.onopen = () => {
    console.log(" Deepgram socket connected");
  };

  socket.onerror = (e) => {
    console.error(" Deepgram socket error", e);
  };

  socket.onclose = () => {
    console.log("Deepgram socket closed");
  };

  socket.onmessage = (msg) => {
    const data = JSON.parse(msg.data);

    const transcript =
      data.channel?.alternatives?.[0]?.transcript;

    if (transcript && data.is_final) {
      console.log("Final transcript:", transcript);
      onFinalTranscript(transcript);
    }
  };

  return socket;
}
