import React from 'react'
import MessageList from './components/MessageList'
import MessageInput from './components/message-input'

export default function Chat() {
  console.log("Chat component rendered")
  return (
    <>
      <MessageList />
      <MessageInput />
    </>
  )
}
