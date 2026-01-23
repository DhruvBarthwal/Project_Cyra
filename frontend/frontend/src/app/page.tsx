// import VoiceAgent from "@/components/VoiceAgent"

import Home from "@/components/Home"

const page = () => {

  return (
    <div className="bg-red-950 relative overflow-hidden h-screen w-screen">
            {/* <div className="absolute left-0 top-1/2 -translate-y-1/2 
                      w-95 h-170 
                      rounded-r-full 
                      bg-red-600 
                      blur-[120px] 
                      z-10
                      opacity-70" /> */}

      {/* Right glow */}
      {/* <div className="absolute right-0 top-1/2 -translate-y-1/2 
                      w-95 h-170 
                      rounded-l-full 
                      bg-red-600 
                      z-10
                      blur-[120px] 
                      opacity-70" /> */}
      <Home/>
    </div>
  )
}

export default page