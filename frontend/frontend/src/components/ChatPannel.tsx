"use client"
import { useTypewriter } from 'react-simple-typewriter'
import {useEffect, useRef} from "react"
import Message from "./Message"
import { ChatMessage } from "@/types/chat"

type ChatProps = {
  messages: ChatMessage[]
}

const ChatPannel = ({ messages }: ChatProps) => {

  const bottomRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({behavior : "smooth"})
  },[messages])

    const  [text]  = useTypewriter({
      words: ["Hi Dhruv! How can I help you? "],
      loop: false,
      typeSpeed: 80,
      deleteSpeed: 30,
      delaySpeed: 2000,
  })
  return (
    <div className=" backdrop-blur-3xl w-1/2 pb-30
                    flex flex-col gap-3 p-4 overflow-y-auto chat-scroll">
      {messages.length === 0 && (
        <p className=" h-full mb-5 flex justify-center items-center text-white text-[40px] text-center font-bold mt-10">
          {text}
        </p>
      )}

      {messages.map((msg) => (
        <Message key={msg.id} {...msg} />
      ))}
    </div>
  )
}

export default ChatPannel
