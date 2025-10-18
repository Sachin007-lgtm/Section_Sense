import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatGPTChatbot from '@/components/ChatGPTChatbot';

const Chat = () => {
  const navigate = useNavigate();

  return (
    <div className="h-[calc(100vh-4rem)] w-full">
      <div className="h-full w-full max-w-[1920px] mx-auto">
        <ChatGPTChatbot isOpen={true} onClose={() => navigate('/')} />
      </div>
    </div>
  );
};

export default Chat;
