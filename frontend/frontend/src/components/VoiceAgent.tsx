"use client";
import { useVoiceAgent } from "@/hooks/useVoiceAgent";
import { speak } from "@/lib/tts";
import AudioOrb from "./AudioOrb";

const VoiceAgent = () => {
  const { start, stop, reset, listening } = useVoiceAgent();

  return (
    <div className="bg-amber-950 rounded-tl-2xl w-1/2 flex flex-col items-center gap-4 justify-center">
      <AudioOrb active={listening} />
      <div className="flex mt-10 gap-10">
        <button
          onClick={() => {
            const u = new SpeechSynthesisUtterance("");
            window.speechSynthesis.speak(u);

            speak("Hi, I am Alex. What would you like to do today?", () => {
              start();
            });
          }}
          className="px-6 py-3 rounded-full cursor-pointer bg-gray-950 text-[#ddc689] hover:bg-gray-900 transition-all"
        >
          Start Alex
        </button>

        {listening && (
          <button
            onClick={stop}
            className="px-6 py-4 cursor-pointer rounded-full bg-gray-800 text-[#ddc689]"
          >
            Stop Listening
          </button>
        )}

        <button
          onClick={reset}
          className="px-8 py-4 cursor-pointer rounded-full bg-red-950 text-[#ddc689] hover:bg-red-900 transition-all"
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
