import React, { useState, useRef } from 'react';
import Header from './components/Header';
import MessageList from './components/MessageList';
import ChatInput from './components/ChatInput';
import { sendMessageToAI } from './services/chatService';
import { UploadCloud } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [pendingFiles, setPendingFiles] = useState([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  const fileInputRef = useRef(null);

  // Add files to the pending list
  const handleAddFiles = (newFiles) => {
    setPendingFiles((prev) => [...prev, ...newFiles]);
  };

  // Remove a pending file by index
  const handleRemoveFile = (index) => {
    setPendingFiles((prev) => prev.filter((_, i) => i !== index));
  };

  // Trigger hidden file picker
  const handleTriggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  // Pre-fill a suggestion prompt from empty state
  const handleSelectPrompt = (promptText) => {
    setInputQuery(promptText);
  };

  // Reset conversation to fresh state
  const handleResetChat = () => {
    setMessages([]);
    setPendingFiles([]);
    setInputQuery('');
  };

  // Send message flow
  const handleSendMessage = async () => {
    const trimmedText = inputQuery.trim();
    if (!trimmedText && pendingFiles.length === 0) return;
    if (isLoading) return;

    const filesToSend = [...pendingFiles];
    const textToSend = trimmedText;

    // 1. Append User Message
    const userMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: textToSend,
      files: filesToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputQuery('');
    setPendingFiles([]);
    setIsLoading(true);

    try {
      // 2. Call Decoupled Service (mock or real API)
      const aiResponse = await sendMessageToAI({
        text: textToSend,
        files: filesToSend,
      });

      const assistantMessage = {
        id: aiResponse.id || (Date.now() + 1).toString(),
        sender: 'assistant',
        text: aiResponse.text,
        timestamp: aiResponse.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to get response:', error);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: `⚠️ **Error communicating with AI service:** ${error.message || 'Unknown error occurred.'} Please check the API configuration in \`src/services/chatService.js\`.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Drag and drop handlers for whole window
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    // Only toggle off if leaving window bounds
    if (e.currentTarget.contains(e.relatedTarget)) return;
    setIsDragOver(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleAddFiles(Array.from(e.dataTransfer.files));
    }
  };

  return (
    <div
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      className="relative flex flex-col h-screen w-full bg-zinc-950 text-zinc-100 overflow-hidden font-sans select-text"
    >
      {/* Drag & Drop Visual Overlay */}
      {isDragOver && (
        <div className="absolute inset-0 z-50 bg-zinc-950/90 backdrop-blur-md border-2 border-dashed border-indigo-500 m-3 rounded-2xl flex flex-col items-center justify-center pointer-events-none transition-all animate-in fade-in duration-150">
          <div className="p-4 rounded-2xl bg-indigo-500/10 text-indigo-400 mb-3 border border-indigo-500/30">
            <UploadCloud className="w-12 h-12 animate-bounce" />
          </div>
          <p className="text-lg font-semibold text-zinc-100">
            Drop documents to attach to your query
          </p>
          <p className="text-xs text-zinc-400 mt-1">
            Supports PDF, DOCX, TXT, CSV, images, and code files
          </p>
        </div>
      )}

      {/* Top Navigation */}
      <Header
        onResetChat={handleResetChat}
        messageCount={messages.length}
      />

      {/* Main Conversation Stream */}
      <main className="flex-1 flex flex-col min-h-0 relative">
        <MessageList
          messages={messages}
          isLoading={isLoading}
          onSelectPrompt={handleSelectPrompt}
          onTriggerFileUpload={handleTriggerFileUpload}
        />

        {/* Floating Input Dock */}
        <ChatInput
          inputQuery={inputQuery}
          setInputQuery={setInputQuery}
          pendingFiles={pendingFiles}
          onAddFiles={handleAddFiles}
          onRemoveFile={handleRemoveFile}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          fileInputRef={fileInputRef}
        />
      </main>
    </div>
  );
}
