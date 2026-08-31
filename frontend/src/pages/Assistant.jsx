import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Paperclip, 
  Trash2, 
  Download, 
  ThumbsUp, 
  ThumbsDown, 
  Globe, 
  Bot, 
  User, 
  FileText, 
  Sparkles, 
  Check, 
  Copy,
  Table as TableIcon,
  Maximize2,
  X,
  Printer
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { askChatQuestion, askChatQuestionWithFile, deleteChatSession, fetchSessionMessages } from '../services/apiService';

const Assistant = ({
  activeDocument,
  activeSessionId,
  sessionTitle = "Conversation",
  onOpenExtractor,
  onClearSession,
  onDeleteSession
}) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [searchWeb, setSearchWeb] = useState(false);
  const [loading, setLoading] = useState(false);
  const [attachedFile, setAttachedFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Initialize warm greeting when a session or document is active
  useEffect(() => {
    if (activeSessionId) {
      loadMessagesForSession(activeSessionId);
    } else {
      initGreeting();
    }
  }, [activeSessionId, activeDocument]);

  const initGreeting = () => {
    const docName = activeDocument?.filename || 'your uploaded document';
    const pages = activeDocument?.page_count || 1;
    const greetingMsg = {
      id: `greet_${Date.now()}`,
      sender: 'assistant',
      text: `👋 **Hello! I'm your Private Multimodal Document Assistant.**\n\nI have indexed **${docName}** (${pages} ${pages === 1 ? 'page' : 'pages'}) across all specialized extractors (Text, Images, Visual Diagrams, Tables, and Equations).\n\n✨ Ask me anything about the document, equations, tables, parameters, or summaries! How can I assist you today? 🚀`,
      timestamp: 'Just now',
      sources: []
    };
    setMessages([greetingMsg]);
  };

  const loadMessagesForSession = async (sId) => {
    try {
      const res = await fetchSessionMessages(sId);
      if (res.messages && res.messages.length > 0) {
        const formatted = [];
        res.messages.forEach((m) => {
          formatted.push({
            id: `usr_${m.id}`,
            sender: 'user',
            text: m.question,
            timestamp: m.created_at ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recent'
          });
          formatted.push({
            id: `ast_${m.id}`,
            sender: 'assistant',
            text: m.answer,
            sources: m.sources || [],
            timestamp: m.created_at ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recent'
          });
        });
        setMessages(formatted);
      } else {
        initGreeting();
      }
    } catch (err) {
      initGreeting();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAttachedFile(file);
      if (file.type.startsWith('image/')) {
        setFilePreview(URL.createObjectURL(file));
      } else {
        setFilePreview(null);
      }
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    if (onClearSession && activeSessionId) onClearSession(activeSessionId);
    initGreeting();
  };

  // Clean, accurately formatted PDF Export
  const handleExportPDF = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const docName = activeDocument?.filename || 'Document';
    const dateStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>${sessionTitle} - AI Document Assistant Export</title>
          <style>
            @page { margin: 20mm; size: A4; }
            body {
              font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
              color: #1a1a1a;
              line-height: 1.6;
              padding: 20px;
            }
            .header {
              border-bottom: 2px solid #6366f1;
              padding-bottom: 15px;
              margin-bottom: 25px;
            }
            .header h1 {
              font-size: 22px;
              color: #312e81;
              margin: 0 0 5px 0;
            }
            .header p {
              font-size: 12px;
              color: #6b7280;
              margin: 0;
            }
            .message-block {
              margin-bottom: 20px;
              padding: 15px 18px;
              border-radius: 12px;
            }
            .user-msg {
              background-color: #f3f4f6;
              border-left: 4px solid #6366f1;
            }
            .ast-msg {
              background-color: #f8fafc;
              border-left: 4px solid #10b981;
              border: 1px solid #e2e8f0;
              border-left-width: 4px;
            }
            .sender-title {
              font-size: 12px;
              font-weight: bold;
              text-transform: uppercase;
              letter-spacing: 0.5px;
              margin-bottom: 6px;
            }
            .user-msg .sender-title { color: #4338ca; }
            .ast-msg .sender-title { color: #065f46; }
            .msg-text {
              font-size: 14px;
              white-space: pre-wrap;
            }
            .sources {
              margin-top: 10px;
              padding-top: 8px;
              border-top: 1px dashed #cbd5e1;
              font-size: 11px;
              color: #64748b;
            }
            table {
              width: 100%;
              border-collapse: collapse;
              margin: 12px 0;
              font-size: 12px;
            }
            th, td {
              border: 1px solid #cbd5e1;
              padding: 6px 10px;
              text-align: left;
            }
            th { background-color: #f1f5f9; font-weight: bold; }
            .footer {
              margin-top: 40px;
              text-align: center;
              font-size: 10px;
              color: #9ca3af;
              border-top: 1px solid #e5e7eb;
              padding-top: 10px;
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>${sessionTitle}</h1>
            <p>Exported from AI Document Assistant • Source Document: <strong>${docName}</strong> • Generated on ${dateStr}</p>
          </div>
          
          <div class="content">
            ${messages.map(m => `
              <div class="message-block ${m.sender === 'user' ? 'user-msg' : 'ast-msg'}">
                <div class="sender-title">${m.sender === 'user' ? 'User Question' : 'Assistant Response'} • ${m.timestamp}</div>
                <div class="msg-text">${m.text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</div>
                ${m.sources && m.sources.length > 0 ? `
                  <div class="sources">
                    <strong>Document Sources Cited:</strong><br/>
                    ${m.sources.map(s => `• Page ${s.page_number || s.page} - ${s.section_name || s.section || 'Specification'}`).join('<br/>')}
                  </div>
                ` : ''}
              </div>
            `).join('')}
          </div>

          <div class="footer">
            MultiDoc RAG • Private Multimodal Offline Assistant • Confidential Document Record
          </div>
          <script>
            window.onload = function() {
              window.print();
            };
          </script>
        </body>
      </html>
    `;

    printWindow.document.write(htmlContent);
    printWindow.document.close();
  };

  const handleSend = async () => {
    if ((!inputValue.trim() && !attachedFile) || loading) return;

    const userQuery = inputValue.trim();
    const currentFile = attachedFile;
    const currentPreview = filePreview;

    const userMsg = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text: userQuery || (currentFile ? `Attached file: ${currentFile.name}` : ''),
      attachedPreview: currentPreview,
      timestamp: 'Just now'
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setAttachedFile(null);
    setFilePreview(null);
    setLoading(true);

    try {
      let res;
      if (currentFile) {
        const formData = new FormData();
        formData.append('question', userQuery || 'Explain and analyze this attached image/file in relation to the document.');
        formData.append('session_id', activeSessionId || 'default_session');
        formData.append('domain', activeDocument?.domain || 'General');
        if (activeDocument?.id) formData.append('document_id', activeDocument.id);
        formData.append('attached_file', currentFile);
        
        const historyPayload = messages.slice(-6).map((m) => ({ sender: m.sender, text: m.text }));
        formData.append('chat_history_json', JSON.stringify(historyPayload));

        res = await askChatQuestionWithFile(formData);
      } else {
        const historyPayload = messages.slice(-6).map((m) => ({ sender: m.sender, text: m.text }));
        res = await askChatQuestion({
          question: userQuery,
          session_id: activeSessionId || 'default_session',
          domain: activeDocument?.domain || 'General',
          document_id: activeDocument?.id || null,
          chat_history: historyPayload
        });
      }

      const result = res.result;

      // Extract table if present
      let extractedTable = null;
      if (result.answer.includes('| --- |') || result.answer.includes('|---|')) {
        const lines = result.answer.split('\n').filter(l => l.trim().startsWith('|'));
        if (lines.length >= 3) {
          const headers = lines[0].split('|').map(c => c.trim()).filter(Boolean);
          const rows = lines.slice(2).map(l => l.split('|').map(c => c.trim()).filter(Boolean));
          extractedTable = {
            title: 'Extracted Parameter Table',
            headers,
            rows
          };
        }
      }

      const astMsg = {
        id: `ast_${Date.now()}`,
        sender: 'assistant',
        text: result.answer,
        sources: result.citations || [],
        tableData: extractedTable,
        externalSuggestions: result.external_suggestions,
        timestamp: 'Just now',
        feedback: null
      };

      setMessages((prev) => [...prev, astMsg]);
    } catch (err) {
      const errorMsg = {
        id: `err_${Date.now()}`,
        sender: 'assistant',
        text: `⚠️ **Apologies!** I encountered a processing error: ${err.response?.data?.detail || err.message || 'Unable to connect to model service'}. Please verify your document is loaded.`,
        timestamp: 'Just now',
        sources: []
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-[#FAF9FD] dark:bg-[#0B0819] overflow-hidden">
      
      {/* Top Header Bar */}
      <header className="h-16 px-8 border-b border-slate-200 dark:border-[#282252] flex items-center justify-between bg-white dark:bg-[#120E24] flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-brand-600 flex items-center justify-center text-white font-bold shadow-sm shadow-brand-500/20">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-sm font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
              <span>{sessionTitle}</span>
              <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                Grounded Mode
              </span>
            </h1>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Target: <strong className="text-brand-600 dark:text-brand-400">{activeDocument?.filename || 'Uploaded Document'}</strong>
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={handleClearChat}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white bg-slate-100 dark:bg-[#1C1638] hover:bg-slate-200 dark:hover:bg-[#281F52] rounded-xl transition-all border border-slate-200 dark:border-[#2E2557]"
            title="Clear current messages"
          >
            <Trash2 className="w-3.5 h-3.5 text-slate-400" />
            <span>Clear Chat</span>
          </button>

          <button
            onClick={handleExportPDF}
            className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-extrabold text-white bg-brand-600 hover:bg-brand-700 rounded-xl transition-all shadow-sm shadow-brand-500/25"
            title="Export clean formatted PDF record"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export PDF</span>
          </button>
        </div>
      </header>

      {/* Messages Workspace */}
      <div className="flex-1 overflow-y-auto px-6 md:px-12 py-6 space-y-6">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-4 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            
            {/* Robot Avatar for Assistant */}
            {msg.sender === 'assistant' && (
              <div className="w-8 h-8 rounded-xl bg-brand-600 text-white flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
                <Bot className="w-4 h-4" />
              </div>
            )}

            {/* Message Bubble Container */}
            <div className={`max-w-3xl ${msg.sender === 'user' ? 'w-auto' : 'w-full'}`}>
              
              {/* User Bubble */}
              {msg.sender === 'user' ? (
                <div className="bg-brand-600 text-white rounded-3xl rounded-tr-sm px-5 py-3.5 text-sm font-medium shadow-md shadow-brand-600/20 space-y-2">
                  {msg.attachedPreview && (
                    <img
                      src={msg.attachedPreview}
                      alt="Attachment preview"
                      className="max-h-40 rounded-xl object-contain bg-black/20 p-1 mb-2"
                    />
                  )}
                  <p className="whitespace-pre-wrap">{msg.text}</p>
                </div>
              ) : (
                /* Assistant Grounded Response Card */
                <div className="bg-white dark:bg-[#15112B] border border-slate-200 dark:border-[#282252] rounded-3xl p-6 shadow-sm space-y-4">
                  
                  {/* Assistant Header & Actions */}
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-[#201A40]">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-extrabold text-brand-600 dark:text-brand-400">
                        AI Document Assistant
                      </span>
                      <span className="text-[10px] text-slate-400 font-medium">
                        {msg.timestamp}
                      </span>
                    </div>

                    {/* Feedback & Copy Actions */}
                    <div className="flex items-center gap-1 text-slate-400">
                      <button
                        onClick={() => handleCopyText(msg.id, msg.text)}
                        className="p-1.5 hover:text-slate-600 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        title="Copy Answer Text"
                      >
                        {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>

                  {/* Grounded Markdown Body with proper math typesetting */}
                  <div className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-sans prose dark:prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.text}
                    </ReactMarkdown>
                  </div>

                  {/* Embedded Structured Table Card */}
                  {msg.tableData && (
                    <div className="border border-slate-200 dark:border-[#282252] rounded-2xl overflow-hidden bg-slate-50/50 dark:bg-[#0D0A1C]/50 mt-3">
                      <div className="px-4 py-2.5 bg-slate-100 dark:bg-[#1A1435] border-b border-slate-200 dark:border-[#282252] flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <TableIcon className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                          <span className="text-xs font-bold text-slate-800 dark:text-white">
                            {msg.tableData.title}
                          </span>
                        </div>
                        {onOpenExtractor && (
                          <button
                            onClick={() => onOpenExtractor('tables')}
                            className="text-[11px] font-extrabold text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1"
                          >
                            <span>View Full Table</span>
                            <Maximize2 className="w-3 h-3" />
                          </button>
                        )}
                      </div>

                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs border-collapse">
                          <thead className="bg-slate-100/60 dark:bg-[#120E24] text-slate-700 dark:text-slate-300 font-bold border-b border-slate-200 dark:border-[#282252]">
                            <tr>
                              {msg.tableData.headers.map((h, i) => (
                                <th key={i} className="py-2.5 px-4">{h}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100 dark:divide-[#201A40]">
                            {msg.tableData.rows.map((row, r_idx) => (
                              <tr key={r_idx} className="hover:bg-purple-50/40 dark:hover:bg-slate-800/30">
                                {row.map((cell, c_idx) => (
                                  <td key={c_idx} className={`py-2 px-4 ${c_idx === 0 ? 'font-bold text-slate-900 dark:text-white' : 'text-slate-600 dark:text-slate-300'}`}>
                                    {cell}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Sources List */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="pt-2 border-t border-slate-100 dark:border-[#201A40]">
                      <p className="text-xs font-extrabold text-slate-500 dark:text-slate-400 mb-1.5 uppercase tracking-wider">
                        Document Sources Cited:
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {msg.sources.map((s, s_idx) => (
                          <span
                            key={s_idx}
                            onClick={() => onOpenExtractor && onOpenExtractor(s.content_type || 'text')}
                            className="px-2.5 py-1 bg-purple-50 dark:bg-[#1E173D] text-brand-700 dark:text-brand-300 border border-brand-200 dark:border-[#2E2557] rounded-lg text-xs font-bold cursor-pointer hover:bg-purple-100 dark:hover:bg-[#281F52] transition-colors"
                          >
                            • Page {s.page_number || s.page || 1} ({s.section_name || s.section || 'Specification'})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                </div>
              )}

            </div>

            {/* User Icon on Right */}
            {msg.sender === 'user' && (
              <div className="w-8 h-8 rounded-xl bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center justify-center flex-shrink-0 mt-1">
                <User className="w-4 h-4" />
              </div>
            )}

          </div>
        ))}

        {/* Loading Bubble */}
        {loading && (
          <div className="flex gap-4 justify-start">
            <div className="w-8 h-8 rounded-xl bg-brand-600 text-white flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 animate-spin" />
            </div>
            <div className="bg-white dark:bg-[#15112B] border border-slate-200 dark:border-[#282252] rounded-3xl p-5 shadow-sm space-y-2">
              <div className="flex items-center gap-2 text-xs font-extrabold text-brand-600 dark:text-brand-400">
                <Sparkles className="w-4 h-4 animate-spin" />
                <span>Reading document & synthesizing grounded response...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Workspace */}
      <div className="p-5 px-6 md:px-12 bg-white dark:bg-[#120E24] border-t border-slate-200 dark:border-[#282252] flex-shrink-0">
        
        {/* Attached File Pill */}
        {attachedFile && (
          <div className="flex items-center gap-2.5 p-2 px-3 mb-3 bg-purple-50 dark:bg-[#1E173D] border border-brand-300 dark:border-[#2E2557] rounded-xl text-xs font-bold text-brand-800 dark:text-brand-300 w-fit">
            <Paperclip className="w-3.5 h-3.5 text-brand-600" />
            <span className="truncate max-w-xs">{attachedFile.name}</span>
            <button
              onClick={() => { setAttachedFile(null); setFilePreview(null); }}
              className="p-0.5 hover:bg-black/10 rounded-full"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        <div className="relative flex items-center bg-slate-50 dark:bg-[#0D0A1C] border border-slate-200 dark:border-[#282252] rounded-2xl p-2 pl-4 focus-within:border-brand-500 transition-colors shadow-inner">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            accept=".pdf,.png,.jpg,.jpeg,.docx,.csv,.xlsx"
          />

          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2 text-slate-400 hover:text-brand-600 dark:hover:text-brand-400 rounded-xl hover:bg-slate-200/50 dark:hover:bg-slate-800 transition-colors mr-2"
            title="Attach Image or Query Document"
          >
            <Paperclip className="w-4 h-4" />
          </button>

          <input
            type="text"
            placeholder="Ask a question about this document, equations, tables, parameters, or summary..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleSend(); }}
            disabled={loading}
            className="flex-1 bg-transparent text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none font-medium"
          />

          <div className="flex items-center gap-3 pr-2">
            <span className="text-[11px] font-bold text-slate-400 hidden sm:inline">
              {inputValue.length}/2000
            </span>

            <button
              onClick={handleSend}
              disabled={(!inputValue.trim() && !attachedFile) || loading}
              className="p-2.5 bg-brand-600 hover:bg-brand-700 disabled:opacity-40 text-white rounded-xl shadow-md shadow-brand-600/30 transition-all cursor-pointer disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Footer Subtext */}
        <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2 px-1 font-medium">
          <span>Targeting {activeDocument?.filename || 'uploaded document'} • Grounded Private RAG</span>
          <span>Open-Source Hugging Face Models</span>
        </div>
      </div>

    </div>
  );
};

export default Assistant;
