import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { MessageCircle } from 'lucide-react';
import { Button } from './ui/button';

export const ChatbotButton: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Don't show the button on the chat page
  if (location.pathname === '/chat') {
    return null;
  }

  return (
    <Button
      onClick={() => navigate('/chat')}
      size="lg"
      className="fixed bottom-6 right-6 h-16 w-16 rounded-2xl transition-all duration-300 z-30 hover:scale-110 p-3 bg-white dark:bg-black border border-gray-200 dark:border-gray-800 shadow-[0_0_20px_rgba(0,0,0,0.3),0_0_40px_rgba(0,0,0,0.1),inset_0_-2px_4px_rgba(0,0,0,0.1)] dark:shadow-[0_0_20px_rgba(255,255,255,0.3),0_0_40px_rgba(255,255,255,0.1),inset_0_-2px_4px_rgba(255,255,255,0.1)] hover:bg-white dark:hover:bg-black"
      aria-label="Open Kamado Chatbot"
    >
      <img 
        src="/chatbot-icon.png" 
        alt="Kamado Chatbot" 
        className="h-full w-full object-contain"
        style={{ filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3))' }}
      />
    </Button>
  );
};
