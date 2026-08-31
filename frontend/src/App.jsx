import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import Sidebar from './components/Sidebar';
import ChatHistoryPanel from './components/ChatHistoryPanel';
import Assistant from './pages/Assistant';
import ExtractorModal from './components/ExtractorModal';
import UploadModal from './components/UploadModal';
import DocumentInfoModal from './components/DocumentInfoModal';
import Login from './pages/Login';
import { fetchDocuments, fetchChatSessions, createChatSession, renameChatSession, deleteChatSession } from './services/apiService';

const MainWorkspace = () => {
  const [documents, setDocuments] = useState([]);
  const [activeDocument, setActiveDocument] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);

  // Modals state
  const [isExtractorOpen, setIsExtractorOpen] = useState(false);
  const [extractorTab, setExtractorTab] = useState('text');
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isDocInfoOpen, setIsDocInfoOpen] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const docsRes = await fetchDocuments();
      const docsList = docsRes.documents || [];
      setDocuments(docsList);
      if (docsList.length > 0) {
        setActiveDocument(docsList[0]);
      }

      const sessRes = await fetchChatSessions();
      if (sessRes && sessRes.sessions) {
        setSessions(sessRes.sessions);
        if (sessRes.sessions.length > 0) {
          setActiveSessionId(sessRes.sessions[0].session_id);
        }
      }
    } catch (err) {
      console.log('Error loading initial data:', err.message);
    }
  };

  const handleOpenExtractor = (tab = 'text') => {
    setExtractorTab(tab);
    setIsExtractorOpen(true);
  };

  const handleUploadSuccess = (newDoc) => {
    if (newDoc) {
      setActiveDocument(newDoc);
      setDocuments((prev) => [newDoc, ...prev.filter(d => d.id !== newDoc.id)]);
    }
  };

  const handleNewSession = async (userChosenTitle) => {
    const title = userChosenTitle || 'New Conversation';
    try {
      const res = await createChatSession(title, activeDocument?.id);
      const newSess = res.session;
      setSessions((prev) => [newSess, ...prev]);
      setActiveSessionId(newSess.session_id);
    } catch (err) {
      const newId = `session_${Date.now()}`;
      const fallbackSess = {
        session_id: newId,
        title: title,
        time: 'Just now'
      };
      setSessions((prev) => [fallbackSess, ...prev]);
      setActiveSessionId(newId);
    }
  };

  const handleRenameSession = async (sessionId, newTitle) => {
    try {
      await renameChatSession(sessionId, newTitle);
      setSessions((prev) =>
        prev.map((s) => (s.session_id === sessionId ? { ...s, title: newTitle } : s))
      );
    } catch (err) {
      setSessions((prev) =>
        prev.map((s) => (s.session_id === sessionId ? { ...s, title: newTitle } : s))
      );
    }
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      await deleteChatSession(sessionId);
      const remaining = sessions.filter((s) => s.session_id !== sessionId);
      setSessions(remaining);
      if (activeSessionId === sessionId) {
        setActiveSessionId(remaining.length > 0 ? remaining[0].session_id : null);
      }
    } catch (err) {
      const remaining = sessions.filter((s) => s.session_id !== sessionId);
      setSessions(remaining);
      if (activeSessionId === sessionId) {
        setActiveSessionId(remaining.length > 0 ? remaining[0].session_id : null);
      }
    }
  };

  const activeSessionObj = sessions.find((s) => s.session_id === activeSessionId);
  const sessionTitle = activeSessionObj?.title || 'AI Document Assistant';

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#F9F9FB] dark:bg-[#0D0A1C] font-sans antialiased text-slate-900 dark:text-slate-100">
      
      {/* 1. Left Dark Navigation Sidebar */}
      <Sidebar
        activeDocument={activeDocument}
        onOpenUpload={() => setIsUploadOpen(true)}
        onOpenDocInfo={() => setIsDocInfoOpen(true)}
        onOpenExtractor={handleOpenExtractor}
        onChangeDocument={() => setIsUploadOpen(true)}
      />

      {/* 2. Middle Chat History Column */}
      <ChatHistoryPanel
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={setActiveSessionId}
        onNewSession={handleNewSession}
        onRenameSession={handleRenameSession}
        onDeleteSession={handleDeleteSession}
      />

      {/* 3. Right Main Assistant Workspace */}
      <main className="flex-1 h-screen flex flex-col overflow-hidden">
        <Assistant
          activeDocument={activeDocument}
          activeSessionId={activeSessionId}
          sessionTitle={sessionTitle}
          onOpenExtractor={handleOpenExtractor}
          onClearSession={handleDeleteSession}
          onDeleteSession={handleDeleteSession}
        />
      </main>

      {/* Extractor Inspector Modal */}
      <ExtractorModal
        isOpen={isExtractorOpen}
        onClose={() => setIsExtractorOpen(false)}
        documentId={activeDocument?.id}
        documentName={activeDocument?.filename}
        initialTab={extractorTab}
      />

      {/* Document Upload Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />

      {/* Document Information Modal */}
      <DocumentInfoModal
        isOpen={isDocInfoOpen}
        onClose={() => setIsDocInfoOpen(false)}
        doc={activeDocument}
      />

    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainWorkspace />
                </ProtectedRoute>
              }
            />
            <Route
              path="/assistant"
              element={
                <ProtectedRoute>
                  <MainWorkspace />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
