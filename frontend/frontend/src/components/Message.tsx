import { ChatMessage } from "@/types/chat"
import ReactMarkdown from "react-markdown"

const Message = ({ role, text }: ChatMessage) => {
  const isAgent = role === "agent"

  return (
    <div
      className={`max-w-[80%] px-4 py-3 mt-2 rounded-2xl text-md
        ${isAgent 
          ? "bg-gray-700 text-amber-100 self-start rounded-tl-none"
          : "bg-green-800 text-white self-end rounded-tr-none"
        }`}
    >
      {isAgent ? (
        <ReactMarkdown
          components={{
            p: ({children}) => <p className="mb-2 last:mb-0">{children}</p>,
            strong: ({children}) => <strong className="font-semibold">{children}</strong>,
            ul: ({children}) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
            ol: ({children}) => <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>,
            li: ({children}) => <li>{children}</li>,
            h1: ({children}) => <h1 className="font-bold text-lg mb-1">{children}</h1>,
            h2: ({children}) => <h2 className="font-bold mb-1">{children}</h2>,
            h3: ({children}) => <h3 className="font-semibold mb-1">{children}</h3>,
          }}
        >
          {text}
        </ReactMarkdown>
      ) : (
        text  
      )}
    </div>
  )
}

export default Message