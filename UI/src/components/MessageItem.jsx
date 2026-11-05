import React, { useState } from 'react';
import { Bot, User, Copy, Check } from 'lucide-react';
import FilePreviewBadge from './FilePreviewBadge';

/**
 * Lightweight helper to format markdown-like text elements:
 * - Code blocks (```)
 * - Inline code (`)
 * - Blockquotes (>)
 * - Bold (**text**)
 * - Unordered lists (- or *)
 * - Headings (###)
 */
function FormattedMessageText({ content }) {
  if (!content) return null;

  // Split by code blocks first
  const parts = content.split(/(```[\s\S]*?```)/g);

  return (
    <div className="space-y-2 text-sm leading-relaxed text-zinc-200">
      {parts.map((part, index) => {
        if (part.startsWith('```') && part.endsWith('```')) {
          const lines = part.slice(3, -3).trim().split('\n');
          const firstLine = lines[0].trim();
          const language = firstLine && !firstLine.includes(' ') ? firstLine : '';
          const codeContent = language ? lines.slice(1).join('\n') : lines.join('\n');

          return (
            <div key={index} className="my-3 rounded-xl overflow-hidden border border-zinc-800 bg-zinc-950/80">
              {language && (
                <div className="px-3.5 py-1.5 bg-zinc-900/90 border-b border-zinc-800 text-[11px] font-mono text-zinc-400 uppercase tracking-wider">
                  {language}
                </div>
              )}
              <pre className="p-3.5 text-xs font-mono text-indigo-200 overflow-x-auto">
                <code>{codeContent}</code>
              </pre>
            </div>
          );
        }

        // Split text by lines to format bullet points, quotes, headings
        const lines = part.split('\n');

        return (
          <div key={index} className="space-y-1.5">
            {lines.map((line, lineIdx) => {
              const trimmed = line.trim();

              if (!trimmed) {
                return <div key={lineIdx} className="h-1.5" />;
              }

              // Headings
              if (trimmed.startsWith('### ')) {
                return (
                  <h4 key={lineIdx} className="text-sm font-bold text-zinc-100 pt-2 pb-1 text-indigo-300">
                    {parseInlineStyles(trimmed.slice(4))}
                  </h4>
                );
              }
              if (trimmed.startsWith('## ')) {
                return (
                  <h3 key={lineIdx} className="text-base font-bold text-zinc-100 pt-2.5 pb-1 text-indigo-200">
                    {parseInlineStyles(trimmed.slice(3))}
                  </h3>
                );
              }

              // Blockquotes
              if (trimmed.startsWith('> ')) {
                return (
                  <blockquote key={lineIdx} className="pl-3 py-1 my-1 border-l-2 border-indigo-500/60 bg-indigo-500/5 text-zinc-300 italic text-xs rounded-r-md">
                    {parseInlineStyles(trimmed.slice(2))}
                  </blockquote>
                );
              }

              // Bullet points
              if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                return (
                  <div key={lineIdx} className="flex items-start gap-2 text-zinc-200 ml-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-2 shrink-0" />
                    <span>{parseInlineStyles(trimmed.slice(2))}</span>
                  </div>
                );
              }

              // Numbered lists (e.g. "1. ")
              const numberedMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
              if (numberedMatch) {
                return (
                  <div key={lineIdx} className="flex items-start gap-2 text-zinc-200 ml-1">
                    <span className="font-mono text-xs text-indigo-400 font-semibold shrink-0 mt-0.5">
                      {numberedMatch[1]}.
                    </span>
                    <span>{parseInlineStyles(numberedMatch[2])}</span>
                  </div>
                );
              }

              // Normal paragraph line
              return (
                <p key={lineIdx} className="text-zinc-200">
                  {parseInlineStyles(trimmed)}
                </p>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

/**
 * Parse bold (**text**) and inline code (`code`)
 */
function parseInlineStyles(text) {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g);

  return parts.map((seg, i) => {
    if (seg.startsWith('`') && seg.endsWith('`')) {
      return (
        <code key={i} className="px-1.5 py-0.5 mx-0.5 rounded-md bg-zinc-800 text-indigo-300 font-mono text-[11px] border border-zinc-700/50">
          {seg.slice(1, -1)}
        </code>
      );
    }
    if (seg.startsWith('**') && seg.endsWith('**')) {
      return (
        <strong key={i} className="font-semibold text-zinc-100">
          {seg.slice(2, -2)}
        </strong>
      );
    }
    return seg;
  });
}

export default function MessageItem({ message }) {
  const isUser = message.sender === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`w-full py-3.5 px-3 sm:px-4 flex gap-3 sm:gap-4 transition-colors ${
      isUser ? 'justify-end' : 'justify-start'
    }`}>
      <div className={`flex gap-3 sm:gap-3.5 max-w-[85%] sm:max-w-[78%] ${
        isUser ? 'flex-row-reverse' : 'flex-row'
      }`}>
        
        {/* Avatar */}
        <div className="shrink-0 mt-0.5">
          {isUser ? (
            <div className="w-8 h-8 rounded-xl bg-zinc-800 border border-zinc-700/80 flex items-center justify-center text-zinc-300 shadow-sm">
              <User className="w-4 h-4" />
            </div>
          ) : (
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-md shadow-indigo-600/20">
              <Bot className="w-4 h-4" />
            </div>
          )}
        </div>

        {/* Bubble & Contents */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} min-w-0`}>
          
          {/* Sender label and timestamp */}
          <div className="flex items-center gap-2 mb-1.5 px-1">
            <span className="text-xs font-medium text-zinc-400">
              {isUser ? 'You' : 'ResearchPilot AI'}
            </span>
            {message.timestamp && (
              <span className="text-[10px] text-zinc-500 font-mono">
                {message.timestamp}
              </span>
            )}
          </div>

          {/* Attached Files (if any) */}
          {message.files && message.files.length > 0 && (
            <div className={`flex flex-wrap gap-2 mb-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
              {message.files.map((file, idx) => (
                <FilePreviewBadge key={idx} file={file} isCompact={false} />
              ))}
            </div>
          )}

          {/* Message Text Bubble */}
          <div
            className={`rounded-2xl px-4 py-3 shadow-sm relative group ${
              isUser
                ? 'bg-indigo-600 text-white rounded-tr-sm border border-indigo-500/40'
                : 'bg-zinc-900/90 text-zinc-100 rounded-tl-sm border border-zinc-800/80 backdrop-blur-sm'
            }`}
          >
            {isUser ? (
              <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                {message.text}
              </p>
            ) : (
              <FormattedMessageText content={message.text} />
            )}

            {/* Copy Button for Assistant responses */}
            {!isUser && (
              <div className="flex justify-end pt-2 mt-2 border-t border-zinc-800/60 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  type="button"
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 px-2 py-1 rounded-md text-[11px] text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/80 transition-colors focus:outline-none"
                  title="Copy response"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400 font-medium">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}

