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

  useEffect(() => {
    const loadVoices = () => window.speechSynthesis.getVoices();
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, []);

  const startAlex = () => {
    const greeting = "Hi, I am Cyra. What would you like to do today?";

    speak(greeting, () => {
      onAgentSpeak("agent", greeting);
      start();
    });
  };

  return (
    <div className="rounded-l-2xl w-1/2 flex flex-col items-center gap-4 justify-center">
      <AudioOrb active={listening} />

      <div className="flex mt-10 gap-10">
        <button
          onClick={startAlex}
          className="px-6 py-3 rounded-full cursor-pointer bg-white text-black hover:bg-amber-200 transition-all duration-300"
        >
          Start Cyra
        </button>

        {listening && (
          <button
            onClick={stop}
            className="px-6 py-4 rounded-full bg-white cursor-pointer text-black hover:bg-amber-200 transition-all duration-300"
          >
            Stop Listening
          </button>
        )}

        <button
          onClick={reset}
          className="px-8 py-4 rounded-full bg-white cursor-pointer text-black hover:bg-amber-200 transition-all duration-300"
        >
          Reset
        </button>
      </div>

      <p className="text-sm text-white">
        {listening ? "Listening..." : ""}
      </p>
    </div>
  );
};

export default VoiceAgent;