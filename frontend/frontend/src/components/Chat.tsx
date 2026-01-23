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
    <div className="flex h-full z-30">
      <VoiceAgent onAgentSpeak={addMessage} onReset={resetChat} />
      <ChatPannel messages={messages} />
    </div>
  )
}

export default Conversation
