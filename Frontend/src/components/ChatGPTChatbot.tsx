import React, { useState, useEffect, useRef } from 'react';
import { Send, Square } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import ChatbotSidebar from './ChatbotSidebar';
import { API_CONFIG } from '@/config/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface Chat {
  id: string;
  title: string;
  timestamp: number;
  messages: Message[];
}

interface ChatGPTChatbotProps {
  isOpen: boolean;
  onClose: () => void;
  initialMessage?: string;
  sectionContext?: {
    code: string;
    title: string;
    description: string;
  };
}

const STORAGE_KEY = 'kamado_chats';

export default function ChatGPTChatbot({ isOpen, onClose, initialMessage, sectionContext }: ChatGPTChatbotProps) {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [contextMessage, setContextMessage] = useState<string>('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Load chats from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsedChats = JSON.parse(saved);
        setChats(parsedChats);
        // Set most recent chat as current
        if (parsedChats.length > 0) {
          setCurrentChatId(parsedChats[0].id);
        }
      } catch (e) {
        console.error('Failed to load chats:', e);
      }
    }
  }, []);

  // Save chats to localStorage whenever they change
  useEffect(() => {
    if (chats.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
    }
  }, [chats]);

  // Handle section context - show greeting without auto-sending
  useEffect(() => {
    if (sectionContext && isOpen) {
      const greeting = `I can help you with **${sectionContext.code} - ${sectionContext.title}**. What would you like to know about this section?`;
      setContextMessage(greeting);
      
      // Create a new chat with just the system greeting
      const newChat: Chat = {
        id: Date.now().toString(),
        title: `${sectionContext.code} Discussion`,
        timestamp: Date.now(),
        messages: [{
          role: 'assistant',
          content: greeting,
          timestamp: new Date().toISOString()
        }]
      };
      setChats(prev => [newChat, ...prev]);
      setCurrentChatId(newChat.id);
    }
  }, [sectionContext, isOpen]);

  // Handle initial message - auto-send when passed directly
  useEffect(() => {
    if (initialMessage && isOpen && !isStreaming && !sectionContext) {
      // Auto-send the message
      const sendInitialMessage = async () => {
        const userMessage: Message = {
          role: 'user',
          content: initialMessage.trim(),
          timestamp: new Date().toISOString()
        };

        // Create new chat
        const newChat: Chat = {
          id: Date.now().toString(),
          title: generateChatTitle(initialMessage),
          timestamp: Date.now(),
          messages: [userMessage]
        };
        setChats(prev => [newChat, ...prev]);
        setCurrentChatId(newChat.id);

        setIsStreaming(true);
        setStreamingContent('');

        try {
          abortControllerRef.current = new AbortController();
          
          const response = await fetch(`${API_CONFIG.BASE_URL}/chatbot/stream`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              message: userMessage.content,
              history: []
            }),
            signal: abortControllerRef.current.signal
          });

          if (!response.ok) {
            throw new Error('Failed to get response');
          }

          const reader = response.body?.getReader();
          const decoder = new TextDecoder();
          let accumulatedContent = '';

          if (reader) {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              const chunk = decoder.decode(value);
              const lines = chunk.split('\n');

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  try {
                    const data = JSON.parse(line.slice(6));
                    
                    if (data.error) {
                      throw new Error(data.error);
                    }
                    
                    if (data.done) {
                      const assistantMessage: Message = {
                        role: 'assistant',
                        content: accumulatedContent,
                        timestamp: new Date().toISOString()
                      };
                      
                      setChats(prev =>
                        prev.map(chat =>
                          chat.id === newChat.id
                            ? { ...chat, messages: [...chat.messages, assistantMessage] }
                            : chat
                        )
                      );
                      
                      setStreamingContent('');
                      setIsStreaming(false);
                      return;
                    }
                    
                    if (data.content) {
                      accumulatedContent += data.content;
                      setStreamingContent(accumulatedContent);
                    }
                  } catch (e) {
                    // Skip invalid JSON
                  }
                }
              }
            }
          }
        } catch (error: any) {
          if (error.name !== 'AbortError') {
            console.error('Auto-send error:', error);
            setStreamingContent('Sorry, an error occurred while processing your request.');
          }
          setIsStreaming(false);
        }
      };

      sendInitialMessage();
    }
  }, [initialMessage, isOpen, sectionContext]);

  const generateChatTitle = (message: string): string => {
    // Take first 50 chars or first sentence
    const title = message.split('\n')[0].substring(0, 50);
    return title.length < message.length ? title + '...' : title;
  };

  const currentChat = chats.find(c => c.id === currentChatId);
  const currentMessages = currentChat?.messages || [];

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [currentMessages, streamingContent]);

  const createNewChat = () => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: 'New Chat',
      timestamp: Date.now(),
      messages: []
    };
    setChats(prev => [newChat, ...prev]);
    setCurrentChatId(newChat.id);
    setInput('');
    setStreamingContent('');
  };

  const selectChat = (chatId: string) => {
    setCurrentChatId(chatId);
    setStreamingContent('');
  };

  const deleteChat = (chatId: string) => {
    setChats(prev => prev.filter(c => c.id !== chatId));
    if (currentChatId === chatId) {
      const remaining = chats.filter(c => c.id !== chatId);
      setCurrentChatId(remaining.length > 0 ? remaining[0].id : null);
    }
  };

  const renameChat = (chatId: string, newTitle: string) => {
    setChats(prev =>
      prev.map(c => (c.id === chatId ? { ...c, title: newTitle } : c))
    );
  };

  const stopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    
    // Save the streaming content as assistant message
    if (streamingContent) {
      const assistantMessage: Message = {
        role: 'assistant',
        content: streamingContent,
        timestamp: new Date().toISOString()
      };
      
      setChats(prev =>
        prev.map(chat =>
          chat.id === currentChatId
            ? { ...chat, messages: [...chat.messages, assistantMessage] }
            : chat
        )
      );
    }
    
    setIsStreaming(false);
    setStreamingContent('');
  };

  const sendMessage = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    // Create new chat if none exists
    let chatId = currentChatId;
    if (!chatId) {
      const newChat: Chat = {
        id: Date.now().toString(),
        title: generateChatTitle(input),
        timestamp: Date.now(),
        messages: [userMessage]
      };
      setChats(prev => [newChat, ...prev]);
      chatId = newChat.id;
      setCurrentChatId(chatId);
    } else {
      // Add user message to current chat
      setChats(prev =>
        prev.map(chat =>
          chat.id === chatId
            ? {
                ...chat,
                messages: [...chat.messages, userMessage],
                title: chat.messages.length === 0 ? generateChatTitle(input) : chat.title,
                timestamp: Date.now()
              }
            : chat
        )
      );
      
      // Move current chat to top
      setChats(prev => {
        const current = prev.find(c => c.id === chatId);
        const others = prev.filter(c => c.id !== chatId);
        return current ? [current, ...others] : prev;
      });
    }

    setInput('');
    setIsStreaming(true);
    setStreamingContent('');

    try {
      abortControllerRef.current = new AbortController();
      
      // Include section context in the message if available
      let messageToSend = userMessage.content;
      if (sectionContext && currentMessages.length <= 2) {
        // Add context only for first few messages in the conversation
        messageToSend = `[Context: I'm asking about ${sectionContext.code} - ${sectionContext.title}]\n\nQuestion: ${userMessage.content}`;
      }
      
      const response = await fetch(`${API_CONFIG.BASE_URL}/chatbot/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageToSend,
          history: currentMessages
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.error) {
                  throw new Error(data.error);
                }
                
                if (data.done) {
                  // Stream complete
                  const assistantMessage: Message = {
                    role: 'assistant',
                    content: accumulatedContent,
                    timestamp: new Date().toISOString()
                  };
                  
                  setChats(prev =>
                    prev.map(chat =>
                      chat.id === chatId
                        ? { ...chat, messages: [...chat.messages, assistantMessage] }
                        : chat
                    )
                  );
                  
                  setStreamingContent('');
                  setIsStreaming(false);
                  return;
                }
                
                if (data.content) {
                  accumulatedContent += data.content;
                  setStreamingContent(accumulatedContent);
                }
              } catch (e) {
                // Skip invalid JSON
              }
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Request aborted');
      } else {
        console.error('Streaming error:', error);
        setStreamingContent('Sorry, an error occurred while processing your request.');
      }
      setIsStreaming(false);
    }
  };

  if (!isOpen) return null;

  const isFullscreen = window.location.pathname === '/chat';

  return (
    <>
      {/* Blur Background Overlay - Only show if not fullscreen */}
      {!isFullscreen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
          onClick={onClose}
        />
      )}
      
      {/* Centered Chatbot Container */}
      <div className={isFullscreen ? "h-full w-full flex" : "fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"}>
        <div className={isFullscreen ? "w-full h-full flex bg-white dark:bg-[#0f1d2e] overflow-hidden" : "w-full max-w-7xl h-[90vh] flex bg-white dark:bg-[#0f1d2e] rounded-2xl shadow-2xl overflow-hidden pointer-events-auto"}>
          {/* Sidebar */}
          <ChatbotSidebar
            chats={chats}
            currentChatId={currentChatId}
            onNewChat={createNewChat}
            onSelectChat={selectChat}
            onDeleteChat={deleteChat}
            onRenameChat={renameChat}
          />

          {/* Main Chat Area */}
          <div className="flex-1 flex flex-col bg-white dark:bg-[#0f1d2e]">
        {/* Header */}
        <div className="h-14 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6 bg-white dark:bg-[#0f1d2e]">
          <h2 className="text-gray-900 dark:text-white font-semibold">
            {currentChat?.title || 'Kamado'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-hidden">
          <div
            ref={scrollRef}
            className="h-full overflow-y-auto"
          >
            {currentMessages.length === 0 && !streamingContent ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-gray-500 dark:text-gray-400 max-w-2xl px-4">
                  <div 
                    className="w-28 h-28 mx-auto mb-6 bg-white dark:bg-black border border-gray-200 dark:border-gray-800 rounded-2xl flex items-center justify-center p-5 shadow-[0_0_30px_rgba(0,0,0,0.35),0_0_60px_rgba(0,0,0,0.2),inset_0_-4px_8px_rgba(0,0,0,0.15)] dark:shadow-[0_0_30px_rgba(255,255,255,0.35),0_0_60px_rgba(255,255,255,0.2),inset_0_-4px_8px_rgba(255,255,255,0.15)]"
                  >
                    <img 
                      src="/chatbot-icon.png" 
                      alt="Kamado" 
                      className="w-full h-full object-contain"
                      style={{ filter: 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.4))' }}
                    />
                  </div>
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                    What's on the agenda today?
                  </h1>
                  <p className="text-lg">
                    Ask me anything about Indian Criminal Law - BNS, BNSS, or BSA
                  </p>
                </div>
              </div>
            ) : (
              <div className="max-w-3xl mx-auto py-8 px-4">
                {currentMessages.map((message, index) => (
                  <div
                    key={index}
                    className={`mb-8 animate-in slide-in-from-bottom-2 fade-in duration-300 ${
                      message.role === 'user' ? 'text-right' : 'text-left'
                    }`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-7 h-7 rounded-lg bg-[#2563eb] flex items-center justify-center p-1">
                          <img 
                            src="/chatbot-icon.png" 
                            alt="Kamado" 
                            className="w-full h-full object-contain"
                          />
                        </div>
                        <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">Kamado</span>
                      </div>
                    )}
                    <div
                      className={`inline-block max-w-[85%] transition-all duration-200 hover:scale-[1.01] ${
                        message.role === 'user'
                          ? 'bg-[#2563eb] text-white rounded-3xl rounded-tr-sm px-6 py-3 shadow-lg hover:shadow-xl'
                          : 'bg-gray-100 dark:bg-[#1a2c42] text-gray-900 dark:text-gray-100 rounded-3xl rounded-tl-sm px-6 py-4 shadow-md hover:shadow-lg'
                      }`}
                    >
                      <div className="whitespace-pre-wrap break-words">
                        {message.content}
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Streaming message */}
                {isStreaming && streamingContent && (
                  <div className="mb-8 text-left animate-in slide-in-from-bottom-2 fade-in duration-300">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-7 h-7 rounded-lg bg-[#2563eb] flex items-center justify-center p-1 animate-pulse">
                        <img 
                          src="/chatbot-icon.png" 
                          alt="Kamado" 
                          className="w-full h-full object-contain"
                        />
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">Kamado is typing...</span>
                    </div>
                    <div className="inline-block max-w-[85%] bg-gray-100 dark:bg-[#1a2c42] text-gray-900 dark:text-gray-100 rounded-3xl rounded-tl-sm px-6 py-4 shadow-md">
                      <div className="whitespace-pre-wrap break-words">
                        {streamingContent}
                        <span className="inline-block w-2 h-4 bg-[#2563eb] animate-pulse ml-1 rounded"></span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-[#0f1d2e] backdrop-blur-sm">
          <div className="max-w-3xl mx-auto">
            <div className="relative flex items-center gap-2 bg-gray-100 dark:bg-[#1a2c42] rounded-3xl px-5 py-3 shadow-lg transition-all duration-200" 
                 style={{
                   borderColor: input ? '#2563eb' : undefined,
                   boxShadow: input ? '0 0 15px rgba(37, 99, 235, 0.2)' : undefined
                 }}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (isStreaming) {
                      stopStreaming();
                    } else {
                      sendMessage();
                    }
                  }
                }}
                placeholder="Type a message..."
                disabled={isStreaming}
                className="flex-1 bg-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 outline-none"
              />
              <Button
                onClick={isStreaming ? stopStreaming : sendMessage}
                disabled={!input.trim() && !isStreaming}
                className={`rounded-full w-10 h-10 p-0 transition-all duration-300 flex items-center justify-center ${
                  isStreaming
                    ? 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 shadow-red-500/50 shadow-lg'
                    : 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 hover:scale-110 shadow-blue-500/50 shadow-lg'
                } text-white disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100`}
              >
                {isStreaming ? (
                  <div className="relative flex items-center justify-center">
                    <Square className="w-4 h-4" fill="currentColor" />
                    <div className="absolute inset-0 rounded-full bg-white/20 animate-ping" />
                  </div>
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-500 text-center mt-2 animate-in fade-in duration-500">
              Kamado can make mistakes. Check important legal information.
            </p>
          </div>
        </div>
      </div> {/* End Main Chat Area */}
        </div> {/* End Chatbot Box */}
      </div> {/* End Centered Container */}
    </>
  );
}
