import React, { useState, useEffect, useRef } from 'react';
import { X, Send, Bot, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { API_CONFIG } from '@/config/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatbotProps {
  isOpen: boolean;
  onClose: () => void;
  initialMessage?: string;
}

export const Chatbot: React.FC<ChatbotProps> = ({ isOpen, onClose, initialMessage }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Load chat history from localStorage
  useEffect(() => {
    const savedChats = localStorage.getItem('kamado_chat_history');
    if (savedChats) {
      const parsed = JSON.parse(savedChats);
      setMessages(parsed.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      })));
    }
  }, []);

  // Save chat history to localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('kamado_chat_history', JSON.stringify(messages));
    }
  }, [messages]);

  // Send initial message if provided
  useEffect(() => {
    if (initialMessage && isOpen && messages.length === 0) {
      handleSendMessage(initialMessage);
    }
  }, [initialMessage, isOpen]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async (messageText?: string) => {
    const textToSend = messageText || input.trim();
    if (!textToSend || isLoading) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: textToSend,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call chatbot API
      const response = await fetch(`${API_CONFIG.BASE_URL}/chatbot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: textToSend,
          history: messages.slice(-10) // Send last 10 messages for context
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Chatbot error:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try again.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem('kamado_chat_history');
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop blur */}
      <div 
        className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 animate-in fade-in duration-200"
        onClick={onClose}
      />

      {/* Chatbot Window */}
      <div className="fixed bottom-4 right-4 w-[400px] h-[600px] bg-background border-2 border-primary/20 rounded-2xl shadow-2xl z-50 flex flex-col animate-in slide-in-from-bottom-4 duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border bg-gradient-to-r from-primary/10 to-primary/5 rounded-t-2xl">
          <div className="flex items-center gap-3">
            <div 
              className="w-12 h-12 rounded-xl bg-white dark:bg-black border border-gray-200 dark:border-gray-800 flex items-center justify-center p-2 shadow-[0_0_15px_rgba(0,0,0,0.25),0_0_30px_rgba(0,0,0,0.1),inset_0_-2px_4px_rgba(0,0,0,0.1)] dark:shadow-[0_0_15px_rgba(255,255,255,0.25),0_0_30px_rgba(255,255,255,0.1),inset_0_-2px_4px_rgba(255,255,255,0.1)]"
            >
              <img 
                src="/chatbot-icon.png" 
                alt="Kamado" 
                className="w-full h-full object-contain"
                style={{ filter: 'drop-shadow(0 2px 3px rgba(0, 0, 0, 0.3))' }}
              />
            </div>
            <div>
              <h3 className="font-bold text-lg">Kamado</h3>
              <p className="text-xs text-muted-foreground">Legal AI Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearChat}
                className="text-xs"
              >
                Clear
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div 
                className="w-24 h-24 mb-6 bg-white dark:bg-black border border-gray-200 dark:border-gray-800 rounded-2xl p-4 shadow-[0_0_25px_rgba(0,0,0,0.3),0_0_50px_rgba(0,0,0,0.15),inset_0_-3px_6px_rgba(0,0,0,0.1)] dark:shadow-[0_0_25px_rgba(255,255,255,0.3),0_0_50px_rgba(255,255,255,0.15),inset_0_-3px_6px_rgba(255,255,255,0.1)]"
              >
                <img 
                  src="/chatbot-icon.png" 
                  alt="Kamado" 
                  className="w-full h-full object-contain"
                  style={{ filter: 'drop-shadow(0 3px 5px rgba(0, 0, 0, 0.4))' }}
                />
              </div>
              <h4 className="font-semibold text-lg mb-2">Welcome to Kamado!</h4>
              <p className="text-sm text-muted-foreground max-w-[280px]">
                I'm your legal AI assistant. Ask me anything about Indian criminal law.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </p>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-2xl px-4 py-2">
                    <Loader2 className="w-5 h-5 animate-spin text-primary" />
                  </div>
                </div>
              )}
            </div>
          )}
        </ScrollArea>

        {/* Input */}
        <div className="p-4 border-t border-border">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask Kamado about legal matters..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              onClick={() => handleSendMessage()}
              disabled={!input.trim() || isLoading}
              size="icon"
              className="shrink-0"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            Powered by AI • For educational purposes
          </p>
        </div>
      </div>
    </>
  );
};
