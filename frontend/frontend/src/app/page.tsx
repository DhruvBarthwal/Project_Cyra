import Home from "@/components/Home"

const page = () => {

  return (
    <div className="relative overflow-hidden h-screen w-screen">
        <div
        className="
          pointer-events-none
          absolute
          top-[-30%]
          left-1/2
          -translate-x-1/2
          w-[120%]
          h-[70%]
          rounded-full
          bg-gray-800
          blur-[120px]
        "
      />
      <Home/>
    </div>
  )
}

export default page