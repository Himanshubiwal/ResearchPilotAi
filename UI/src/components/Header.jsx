import React from 'react';
import { Bot, Sparkles, RotateCcw, PlugZap } from 'lucide-react';

export default function Header({ onResetChat, messageCount }) {
  return (
    <header className="sticky top-0 z-20 w-full border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-xl">
      <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
        
        {/* Brand / Logo */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-500 shadow-md shadow-indigo-500/20 text-white">
            <Bot className="w-5 h-5" />
            <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-400 rounded-full border-2 border-zinc-950" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-semibold text-sm sm:text-base tracking-tight text-zinc-100 flex items-center gap-1.5">
                ResearchPilot <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent font-bold">AI</span>
              </h1>
              <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                <Sparkles className="w-2.5 h-2.5" /> v1.0
              </span>
            </div>
            <p className="text-[11px] text-zinc-400 hidden sm:block">
              Intelligent Document Analysis & Question Answering
            </p>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2.5">
          {/* API Status Badge */}
          <div 
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-zinc-900 border border-zinc-800 text-[11px] text-zinc-400 font-medium"
            title="Connected to FastAPI backend on port 8000"
          >
            <PlugZap className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden md:inline text-zinc-300">FastAPI API</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          </div>

          {/* New Chat Button */}
          {messageCount > 0 && (
            <button
              onClick={onResetChat}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white border border-zinc-800 transition-all text-xs font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
              title="Start a fresh conversation"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>New Chat</span>
            </button>
          )}
        </div>

      </div>
    </header>
  );
}

