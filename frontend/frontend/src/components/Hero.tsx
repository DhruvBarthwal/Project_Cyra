import React, { useState } from "react";
import { IoMdMail } from "react-icons/io";
import { useEffect } from "react";

type HeroProps = {
  onStart: () => void;
};

const Hero: React.FC<HeroProps> = ({ onStart }) => {
  const [show, setShow] = useState(false);

  useEffect(() => {
    setShow(true);
  }, []);

  return (
    <div
      className={`text-white w-full h-175 flex flex-col gap-5 justify-center items-center transition-all duration-1000 ease-out ${show ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
    >
      <div className="hero-heading text-black text-7xl font-bold">
        <h1 className="flex justify-center items-center">
          Tired of Typing E<IoMdMail size={58} />
          ails?
        </h1>
      </div>
      <div className="text-2xl text-black">
        <h1>Manage your emails using just your voice.</h1>
      </div>
      <div className="mt-2">
        <button
          onClick={onStart}
          className="border border-[#D8B75E] shadow-red-500 bg-gray-950 hover:bg-gray-800 transition-all duration-300 p-3 px-10 cursor-pointer rounded-2xl text-[19px]"
        >
          Get Started
        </button>
      </div>
    </div>
  );
};

export default Hero;
