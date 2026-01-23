export type Message = {
    role : "user" | "assistant";
    content : string;
}

export type ChatMessage = {
  id: string
  role: "user" | "agent"
  text: string
}