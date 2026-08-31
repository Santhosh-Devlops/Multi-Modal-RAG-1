import React, { useState } from 'react';
import { Search, MessageSquare, Plus, Trash2, Edit2, Check, X } from 'lucide-react';

const ChatHistoryPanel = ({
  sessions = [],
  activeSessionId,
  onSelectSession,
  onNewSession,
  onRenameSession,
  onDeleteSession
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [isCreatingNew, setIsCreatingNew] = useState(false);
  const [newTitle, setNewTitle] = useState('');

  const handleStartRename = (session, e) => {
    e.stopPropagation();
    setEditingId(session.session_id);
    setEditTitle(session.title);
  };

  const handleSaveRename = (sessionId, e) => {
    e.stopPropagation();
    if (editTitle.trim() && onRenameSession) {
      onRenameSession(sessionId, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleCreateNew = (e) => {
    e.preventDefault();
    if (newTitle.trim() && onNewSession) {
      onNewSession(newTitle.trim());
      setNewTitle('');
      setIsCreatingNew(false);
    }
  };

  const filteredSessions = sessions.filter((s) =>
    (s.title || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <aside className="w-80 h-screen flex flex-col bg-white dark:bg-[#120E24] border-r border-slate-200 dark:border-[#282252] flex-shrink-0 transition-colors">
      
      {/* Header */}
      <div className="p-5 pb-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-extrabold text-slate-900 dark:text-white">Chat History</h2>
          <span className="text-[11px] font-extrabold text-slate-400 px-2 py-0.5 rounded-full bg-slate-100 dark:bg-[#1A1435]">
            {sessions.length} {sessions.length === 1 ? 'chat' : 'chats'}
          </span>
        </div>
        
        {/* Search Input */}
        <div className="relative mt-3">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 dark:bg-[#0D0A1C] border border-slate-200 dark:border-[#282252] rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-brand-500 transition-colors font-medium"
          />
        </div>
      </div>

      {/* New Conversation Creation Prompt (If active) */}
      {isCreatingNew && (
        <form onSubmit={handleCreateNew} className="p-3 mx-4 mb-2 bg-purple-50 dark:bg-[#1A1435] border border-brand-300 dark:border-brand-700/60 rounded-2xl space-y-2">
          <p className="text-[11px] font-bold text-brand-700 dark:text-brand-300">Name Your Conversation</p>
          <input
            type="text"
            placeholder="e.g. Methodology & Equations"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            autoFocus
            className="w-full px-3 py-1.5 text-xs bg-white dark:bg-[#0D0A1C] border border-slate-200 dark:border-[#282252] rounded-lg text-slate-900 dark:text-white focus:outline-none focus:border-brand-500"
          />
          <div className="flex items-center justify-end gap-2 pt-1">
            <button
              type="button"
              onClick={() => setIsCreatingNew(false)}
              className="px-2.5 py-1 text-xs text-slate-500 hover:text-slate-700 dark:text-slate-400 font-bold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!newTitle.trim()}
              className="px-3 py-1 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-extrabold shadow-sm"
            >
              Start Chat
            </button>
          </div>
        </form>
      )}

      {/* Session List */}
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-2">
        {filteredSessions.length === 0 ? (
          <div className="text-center py-12 px-4">
            <MessageSquare className="w-8 h-8 text-slate-300 dark:text-slate-600 mx-auto mb-2" />
            <p className="text-xs font-bold text-slate-600 dark:text-slate-400">No saved conversations yet</p>
            <p className="text-[11px] text-slate-400 mt-1">Start a conversation based on your uploaded document.</p>
          </div>
        ) : (
          filteredSessions.map((item) => {
            const isActive = activeSessionId === item.session_id;
            const isEditing = editingId === item.session_id;

            return (
              <div
                key={item.session_id}
                onClick={() => onSelectSession(item.session_id)}
                className={`group relative p-3.5 rounded-2xl cursor-pointer transition-all border ${
                  isActive
                    ? 'bg-purple-50/80 dark:bg-[#201842] border-brand-300 dark:border-brand-600 text-brand-900 dark:text-white shadow-sm'
                    : 'bg-white dark:bg-transparent border-transparent hover:bg-slate-50 dark:hover:bg-slate-800/40 text-slate-700 dark:text-slate-300'
                }`}
              >
                {isEditing ? (
                  <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      autoFocus
                      className="flex-1 px-2 py-1 text-xs bg-white dark:bg-[#0D0A1C] border border-brand-500 rounded-lg text-slate-900 dark:text-white"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSaveRename(item.session_id, e);
                        if (e.key === 'Escape') setEditingId(null);
                      }}
                    />
                    <button
                      onClick={(e) => handleSaveRename(item.session_id, e)}
                      className="p-1 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 rounded-md"
                      title="Save"
                    >
                      <Check className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); setEditingId(null); }}
                      className="p-1 text-slate-400 hover:text-slate-600 rounded-md"
                      title="Cancel"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ) : (
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <h4 className={`text-xs font-extrabold truncate ${isActive ? 'text-brand-900 dark:text-white' : 'text-slate-800 dark:text-slate-200'}`}>
                        {item.title}
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-1 font-medium">
                        {item.time || 'Active Session'}
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      {onRenameSession && (
                        <button
                          onClick={(e) => handleStartRename(item, e)}
                          className="p-1 text-slate-400 hover:text-brand-600 dark:hover:text-brand-400"
                          title="Rename Conversation"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                      {onDeleteSession && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteSession(item.session_id);
                          }}
                          className="p-1 text-slate-400 hover:text-red-500"
                          title="Delete Conversation"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Bottom New Conversation Button */}
      <div className="p-4 border-t border-slate-200 dark:border-[#282252]">
        <button
          onClick={() => setIsCreatingNew(true)}
          className="w-full py-2.5 px-4 rounded-2xl border border-brand-300 dark:border-brand-700/60 bg-purple-50/70 dark:bg-[#1E163B] hover:bg-purple-100 dark:hover:bg-[#281E4E] text-brand-700 dark:text-brand-300 font-extrabold text-xs flex items-center justify-center gap-2 transition-all shadow-sm"
        >
          <Plus className="w-4 h-4 text-brand-600 dark:text-brand-400" />
          <span>+ New Named Conversation</span>
        </button>
      </div>

    </aside>
  );
};

export default ChatHistoryPanel;
