import React from 'react'
import VoiceAgent from './VoiceAgent'
import Message from './Message'

const Chat = () => {
  return (
    <div className='text-white w-full h-166 flex'>
        <VoiceAgent/>
        <Message/>
    </div>
  )
}

export default Chat