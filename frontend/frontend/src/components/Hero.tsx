import React from 'react'

type HeroProps = {
    onStart: () => void
}

const Hero: React.FC<HeroProps> = ({ onStart }) => {
  return (
    <div className='text-white w-full h-175 flex flex-col gap-5 justify-center items-center'>
        <div className='hero-heading text-[#d3bb79] text-7xl font-bold'>
            <h1>Meet Alex</h1>
        </div>
        <div className='text-2xl text-[#D8B75E]'>
            <h1>Manage your emails using just your voice.</h1>
        </div>
        <div className='mt-2'>
            <button
                onClick = {onStart}
                className='border border-[#D8B75E] shadow-red-500 bg-red-800 hover:bg-red-700 transition-all p-3 px-10 cursor-pointer rounded-2xl text-[19px]'
            >
                Get Started
            </button>
        </div>
    </div>
  )
}

export default Hero