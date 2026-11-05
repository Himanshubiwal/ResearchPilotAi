import React, { useRef, useEffect } from 'react';
import { Paperclip, ArrowUp, FileUp } from 'lucide-react';
import FilePreviewBadge from './FilePreviewBadge';

export default function ChatInput({
  inputQuery,
  setInputQuery,
  pendingFiles,
  onAddFiles,
  onRemoveFile,
  onSendMessage,
  isLoading,
  fileInputRef,
}) {
  const textareaRef = useRef(null);

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [inputQuery]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && (inputQuery.trim() || pendingFiles.length > 0)) {
        onSendMessage();
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onAddFiles(Array.from(e.target.files));
      e.target.value = ''; // Reset input to allow re-uploading same file
    }
  };

  const canSubmit = !isLoading && (inputQuery.trim().length > 0 || pendingFiles.length > 0);

  return (
    <div className="w-full max-w-4xl mx-auto px-3 sm:px-4 pb-4 sm:pb-6 pt-2">
      <div className="relative rounded-2xl bg-zinc-900/90 border border-zinc-800 shadow-2xl backdrop-blur-xl transition-all focus-within:border-indigo-500/60 focus-within:ring-2 focus-within:ring-indigo-500/20">
        
        {/* Hidden native file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt,.csv,.xls,.xlsx,.md,.json,.png,.jpg,.jpeg"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Pending Attached Files Strip */}
        {pendingFiles.length > 0 && (
          <div className="p-2.5 pb-0 flex flex-wrap gap-2 border-b border-zinc-850">
            {pendingFiles.map((file, idx) => (
              <FilePreviewBadge
                key={idx}
                file={file}
                onRemove={() => onRemoveFile(idx)}
              />
            ))}
          </div>
        )}

        {/* Text Input Row */}
        <div className="flex items-end gap-2 p-2 sm:p-2.5">
          {/* File Upload Button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="p-2 rounded-xl text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-all shrink-0 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            title="Attach document or research file (.pdf, .docx, .txt, .csv, etc.)"
          >
            <Paperclip className="w-5 h-5" />
          </button>

          {/* Query Textarea */}
          <textarea
            ref={textareaRef}
            rows={1}
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              pendingFiles.length > 0
                ? "Ask a question about the attached document(s)..."
                : "Ask any research question or upload a document..."
            }
            className="flex-1 max-h-[180px] py-1.5 px-2 bg-transparent text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none resize-none leading-relaxed"
          />

          {/* Send Button */}
          <button
            type="button"
            onClick={onSendMessage}
            disabled={!canSubmit}
            className={`p-2.5 rounded-xl transition-all shrink-0 flex items-center justify-center focus:outline-none ${
              canSubmit
                ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30 active:scale-95'
                : 'bg-zinc-850 text-zinc-600 cursor-not-allowed'
            }`}
            title="Send query (Enter)"
          >
            <ArrowUp className="w-4 h-4 stroke-[2.5]" />
          </button>
        </div>

      </div>

      {/* Helpful Hint Bar */}
      <div className="flex items-center justify-between text-[11px] text-zinc-500 px-2 pt-2">
        <span className="flex items-center gap-1.5">
          <FileUp className="w-3.5 h-3.5 text-zinc-400" />
          <span>Upload PDF, Word, TXT, CSV, or images</span>
        </span>
        <span className="hidden sm:inline">
          <kbd className="px-1 py-0.5 rounded bg-zinc-850 border border-zinc-750 text-[10px] text-zinc-400">Enter</kbd> to send, <kbd className="px-1 py-0.5 rounded bg-zinc-850 border border-zinc-750 text-[10px] text-zinc-400">Shift + Enter</kbd> for new line
        </span>
      </div>
    </div>
  );
}

