let cachedVoice: SpeechSynthesisVoice | null = null;

function getMaleFriendlyVoice(): SpeechSynthesisVoice | null {
  const voices = window.speechSynthesis.getVoices();

  // Priority list (best → fallback)
  const preferred = [
    "Google UK English Male",
    "Google US English",
    "Microsoft David",
    "Microsoft Mark",
    "Alex", // macOS
  ];

  for (const name of preferred) {
    const voice = voices.find(v =>
      v.name.toLowerCase().includes(name.toLowerCase())
    );
    if (voice) return voice;
  }

  // Fallback: any English male-ish voice
  return voices.find(v => v.lang.startsWith("en")) || null;
}

export function speak(text: string, onEnd?: () => void) {
  const utterance = new SpeechSynthesisUtterance(text);

  if (!cachedVoice) {
    cachedVoice = getMaleFriendlyVoice();
  }

  if (cachedVoice) {
    utterance.voice = cachedVoice;
  }

  // 🎛 Friendly tuning
  utterance.rate = 0.95;   // slightly slower = calmer
  utterance.pitch = 0.9;   // lower pitch = male
  utterance.volume = 1.0;

  utterance.onend = () => {
    onEnd?.();
  };

  window.speechSynthesis.cancel(); // stop overlaps
  window.speechSynthesis.speak(utterance);
}