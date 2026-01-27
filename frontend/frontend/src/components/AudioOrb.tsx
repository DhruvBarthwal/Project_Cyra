"use client";
import { useEffect, useState } from "react";

const AudioOrb = ({ active }: { active: boolean }) => {
  const [scale, setScale] = useState(1);

  useEffect(() => {
    if (!active) {
      setScale(1);
      return;
    }

    let audioCtx: AudioContext | null = null;
    let analyser: AnalyserNode | null = null;
    let dataArray: Uint8Array<ArrayBuffer>;
    let rafId = 0;

    const startAudio = async () => {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      audioCtx = new AudioContext();
      const source = audioCtx.createMediaStreamSource(stream);

      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;

      const buffer = new ArrayBuffer(analyser.frequencyBinCount);
      dataArray = new Uint8Array(buffer);

      source.connect(analyser);

      const animate = () => {
        if (!analyser) return;

        analyser.getByteFrequencyData(dataArray);

        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }

        const volume = sum / dataArray.length;
        const newScale = 1 + Math.min(volume / 120, 0.6);

        setScale(newScale);
        rafId = requestAnimationFrame(animate);
      };

      animate();
    };

    startAudio();

    return () => {
      cancelAnimationFrame(rafId);
      audioCtx?.close();
    };
  }, [active]);

  return (
    <div
      className="h-60 w-60 rounded-full 
                 bg-linear-to-br from-[#ffffff] via-[#c3c1de] to-[#370873]
                 transition-transform duration-75"
      style={{ transform: `scale(${scale})` }}
    />
  );
};

export default AudioOrb;
