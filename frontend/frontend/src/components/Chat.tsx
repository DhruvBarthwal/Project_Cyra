"use client"
import { useState } from "react"
import VoiceAgent from "./VoiceAgent"
import { ChatMessage } from "@/types/chat"
import ChatPannel from "./ChatPannel"

const Conversation = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([])

  const addMessage = (role: "user" | "agent", text: string) => {
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role, text }
    ])
  }

  const resetChat = () => setMessages([])

  return (
    <div className="bg-gray-950 backdrop-blur-2xl flex h-full z-3">
      <div
        className="pointer-events-none absolute left-[-30%] top-1/2 -translate-y-1/2 w-[60%] h-[60%] rounded-full bg-cyan-400/20 blur-[140px]"
      />
      <div
        className="
          pointer-events-none absolute right-[-30%] top-1/2 -translate-y-1/2 w-[60%] h-[60%] rounded-full bg-amber-400/25 blur-[140px]"
      />

      <VoiceAgent onAgentSpeak={addMessage} onReset={resetChat} />
      <ChatPannel messages={messages} />
    </div>
  )
}

export default Conversation
