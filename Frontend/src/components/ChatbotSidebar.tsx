import React from 'react';
import { MessageCircle, Search, Library, FolderKanban, Plus, Trash2, Edit2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';

interface Chat {
  id: string;
  title: string;
  timestamp: number;
  messages: any[];
}

interface ChatbotSidebarProps {
  chats: Chat[];
  currentChatId: string | null;
  onNewChat: () => void;
  onSelectChat: (chatId: string) => void;
  onDeleteChat: (chatId: string) => void;
  onRenameChat: (chatId: string, newTitle: string) => void;
}

export default function ChatbotSidebar({
  chats,
  currentChatId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  onRenameChat
}: ChatbotSidebarProps) {
  const [searchQuery, setSearchQuery] = React.useState('');
  const [editingChatId, setEditingChatId] = React.useState<string | null>(null);
  const [editTitle, setEditTitle] = React.useState('');

  const filteredChats = chats.filter(chat =>
    chat.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleRename = (chatId: string) => {
    if (editTitle.trim()) {
      onRenameChat(chatId, editTitle.trim());
      setEditingChatId(null);
      setEditTitle('');
    }
  };

  const startEdit = (chat: Chat) => {
    setEditingChatId(chat.id);
    setEditTitle(chat.title);
  };

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  // Group chats by time period
  const groupedChats = React.useMemo(() => {
    const today: Chat[] = [];
    const yesterday: Chat[] = [];
    const lastWeek: Chat[] = [];
    const older: Chat[] = [];

    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const yesterdayStart = todayStart - 24 * 60 * 60 * 1000;
    const lastWeekStart = todayStart - 7 * 24 * 60 * 60 * 1000;

    filteredChats.forEach(chat => {
      if (chat.timestamp >= todayStart) {
        today.push(chat);
      } else if (chat.timestamp >= yesterdayStart) {
        yesterday.push(chat);
      } else if (chat.timestamp >= lastWeekStart) {
        lastWeek.push(chat);
      } else {
        older.push(chat);
      }
    });

    return { today, yesterday, lastWeek, older };
  }, [filteredChats]);

  const renderChatItem = (chat: Chat) => {
    const isActive = chat.id === currentChatId;
    const isEditing = editingChatId === chat.id;

    // Truncate title to 10 words
    const truncateTitle = (title: string) => {
      const words = title.split(' ');
      if (words.length > 10) {
        return words.slice(0, 10).join(' ') + '...';
      }
      return title;
    };

    return (
      <div
        key={chat.id}
        className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-all ${
          isActive
            ? 'bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800/50'
        }`}
        onClick={() => !isEditing && onSelectChat(chat.id)}
      >
        <MessageCircle className="w-4 h-4 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          {isEditing ? (
            <Input
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleRename(chat.id);
                if (e.key === 'Escape') setEditingChatId(null);
              }}
              onBlur={() => handleRename(chat.id)}
              className="h-6 bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm"
              autoFocus
              onClick={(e) => e.stopPropagation()}
            />
          ) : (
            <span className="text-sm block" title={chat.title}>
              {truncateTitle(chat.title)}
            </span>
          )}
        </div>
        {!isEditing && (
          <div className="flex items-center gap-1 flex-shrink-0">
            <button
              onClick={(e) => {
                e.stopPropagation();
                startEdit(chat);
              }}
              className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
              title="Rename"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (confirm('Delete this chat?')) {
                  onDeleteChat(chat.id);
                }
              }}
              className="p-1.5 hover:bg-red-600/20 rounded text-red-400 hover:text-red-300 transition-colors"
              title="Delete"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-80 bg-gray-50 dark:bg-[#0a1525] text-gray-900 dark:text-white flex flex-col h-full border-r border-gray-200 dark:border-gray-800">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <Button
          onClick={onNewChat}
          className="w-full bg-transparent border border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-900 dark:text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Chat
        </Button>
      </div>

      {/* Search */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
          <Input
            placeholder="Search chats"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
          />
        </div>
      </div>

      {/* Navigation Links */}
      <div className="px-4 py-2 space-y-1">
        <button className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
          <Library className="w-4 h-4" />
          <span className="text-sm">Library</span>
        </button>
        <button className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
          <FolderKanban className="w-4 h-4" />
          <span className="text-sm">Projects</span>
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full px-4 py-2">
          <div className="space-y-4">
            {groupedChats.today.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 mb-2">Today</h3>
                <div className="space-y-1">
                  {groupedChats.today.map(renderChatItem)}
                </div>
              </div>
            )}

            {groupedChats.yesterday.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 mb-2">Yesterday</h3>
                <div className="space-y-1">
                  {groupedChats.yesterday.map(renderChatItem)}
                </div>
              </div>
            )}

            {groupedChats.lastWeek.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 mb-2">Previous 7 Days</h3>
                <div className="space-y-1">
                  {groupedChats.lastWeek.map(renderChatItem)}
                </div>
              </div>
            )}

            {groupedChats.older.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 mb-2">Older</h3>
                <div className="space-y-1">
                  {groupedChats.older.map(renderChatItem)}
                </div>
              </div>
            )}

            {filteredChats.length === 0 && (
              <div className="text-center text-gray-400 dark:text-gray-500 text-sm py-8">
                {searchQuery ? 'No chats found' : 'No chats yet'}
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-800">
        <div className="text-xs text-gray-400 dark:text-gray-500 text-center">
          Kamado Legal Assistant
        </div>
      </div>
    </div>
  );
}
