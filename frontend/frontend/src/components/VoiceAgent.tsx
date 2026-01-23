"use client";
import { useVoiceAgent } from "@/hooks/useVoiceAgent";
import { speak } from "@/lib/tts";
import AudioOrb from "./AudioOrb";
import { useEffect } from "react";

type VoiceAgentProps = {
  onAgentSpeak: (role: "user" | "agent", text: string) => void;
  onReset: () => void;
};

const VoiceAgent = ({ onAgentSpeak, onReset }: VoiceAgentProps) => {
  const { start, stop, reset, listening } = useVoiceAgent(onAgentSpeak);

  // ✅ Ensure voices are loaded BEFORE speaking
  useEffect(() => {
    const loadVoices = () => window.speechSynthesis.getVoices();
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, []);

  const startAlex = () => {
    const greeting = "Hi, I am Alex. What would you like to do today?";

    speak(greeting, () => {
      onAgentSpeak("agent", greeting);
      start();
    });
  };

  return (
    <div className="bg-amber-950 rounded-tl-2xl w-1/2 flex flex-col items-center gap-4 justify-center">
      <AudioOrb active={listening} />

      <div className="flex mt-10 gap-10">
        <button
          onClick={startAlex}
          className="px-6 py-3 rounded-full cursor-pointer bg-gray-950 text-[#ddc689] hover:bg-gray-900"
        >
          Start Alex
        </button>

        {listening && (
          <button
            onClick={stop}
            className="px-6 py-4 rounded-full cursor-pointer bg-gray-800 text-[#ddc689]"
          >
            Stop Listening
          </button>
        )}

        <button
          onClick={reset}
          className="px-8 py-4 rounded-full bg-red-950 cursor-pointer text-[#ddc689] hover:bg-red-900"
        >
          Reset
        </button>
      </div>

      <p className="text-sm text-gray-500">
        {listening ? "Listening..." : ""}
      </p>
    </div>
  );
};

export default VoiceAgent;