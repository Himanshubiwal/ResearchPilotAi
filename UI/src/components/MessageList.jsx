import React, { useEffect, useRef } from 'react';
import MessageItem from './MessageItem';
import EmptyState from './EmptyState';
import { Bot, Loader2 } from 'lucide-react';

export default function MessageList({
  messages,
  isLoading,
  onSelectPrompt,
  onTriggerFileUpload,
}) {
  const bottomRef = useRef(null);

  // Auto-scroll on messages change or when loading begins
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (messages.length === 0) {
    return (
      <EmptyState
        onSelectPrompt={onSelectPrompt}
        onTriggerFileUpload={onTriggerFileUpload}
      />
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-2 sm:px-4 py-4 space-y-2">
      <div className="max-w-4xl mx-auto w-full">
        {messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}

        {/* Loading / Thinking Indicator */}
        {isLoading && (
          <div className="py-3 px-3 sm:px-4 flex gap-3 sm:gap-4 justify-start">
            <div className="flex gap-3 sm:gap-3.5 max-w-[85%] items-start">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-md shadow-indigo-600/20 shrink-0">
                <Bot className="w-4 h-4" />
              </div>

              <div className="flex flex-col items-start min-w-0">
                <div className="flex items-center gap-2 mb-1.5 px-1">
                  <span className="text-xs font-medium text-zinc-400">ResearchPilot AI</span>
                  <span className="text-[10px] text-indigo-400 animate-pulse font-medium">Processing...</span>
                </div>

                <div className="rounded-2xl px-4 py-3 bg-zinc-900/90 border border-zinc-800/80 rounded-tl-sm flex items-center gap-3">
                  <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
                  <span className="text-xs text-zinc-300">
                    Analyzing documents and generating response...
                  </span>
                  <div className="flex gap-1 ml-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce [animation-delay:-0.3s]" />
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce [animation-delay:-0.15s]" />
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} className="h-4" />
      </div>
    </div>
  );
}

