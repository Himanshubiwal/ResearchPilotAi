import React from 'react';
import { 
  FileSearch, 
  Sparkles, 
  UploadCloud, 
  FileText, 
  HelpCircle, 
  CheckCircle2 
} from 'lucide-react';

const SUGGESTED_QUERIES = [
  {
    icon: FileSearch,
    title: 'Summarize key findings',
    desc: 'Extract main arguments, methodologies, and conclusions from your documents.',
    prompt: 'Can you summarize the key findings and conclusions in the uploaded document?',
  },
  {
    icon: HelpCircle,
    title: 'Ask specific questions',
    desc: 'Query details, tables, metrics, or quotes inside your research files.',
    prompt: 'What are the main statistics and evidence presented to support the claims?',
  },
  {
    icon: FileText,
    title: 'Extract action items',
    desc: 'Break down complex research into clear, structured bullet points.',
    prompt: 'Extract the top 5 takeaways and actionable recommendations from this text.',
  },
  {
    icon: CheckCircle2,
    title: 'Critique & verify claims',
    desc: 'Identify assumptions, limitations, and potential gaps in the findings.',
    prompt: 'What are the potential limitations and critical assumptions made in this paper?',
  },
];

export default function EmptyState({ onSelectPrompt, onTriggerFileUpload }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 sm:p-8 max-w-3xl mx-auto w-full text-center my-auto">
      
      {/* Hero Badge & Title */}
      <div className="relative mb-6">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500/20 via-violet-500/10 to-transparent border border-indigo-500/30 flex items-center justify-center mx-auto shadow-inner shadow-indigo-500/20">
          <Sparkles className="w-8 h-8 text-indigo-400" />
        </div>
      </div>

      <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-zinc-100 mb-2">
        How can I help with your research today?
      </h2>
      <p className="text-sm sm:text-base text-zinc-400 max-w-lg mb-8">
        Upload documents or ask questions directly. I can analyze papers, extract data, synthesize summaries, and answer any query.
      </p>

      {/* Quick Upload Callout Box */}
      <div 
        onClick={onTriggerFileUpload}
        className="w-full mb-8 p-4 rounded-2xl border-2 border-dashed border-zinc-800 hover:border-indigo-500/50 bg-zinc-900/40 hover:bg-zinc-900/70 transition-all cursor-pointer flex flex-col sm:flex-row items-center justify-between gap-4 group"
      >
        <div className="flex items-center gap-3.5 text-left">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 group-hover:bg-indigo-500 group-hover:text-white transition-all">
            <UploadCloud className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs sm:text-sm font-semibold text-zinc-200 group-hover:text-white">
              Drop documents here or click to browse
            </p>
            <p className="text-[11px] text-zinc-500">
              Supports PDF, DOCX, TXT, CSV, MD, and images (multiple files allowed)
            </p>
          </div>
        </div>
        <span className="text-xs px-3 py-1.5 rounded-lg bg-zinc-800 text-zinc-300 border border-zinc-700/60 group-hover:border-indigo-500/40 font-medium">
          Choose Files
        </span>
      </div>

      {/* Suggested Starters Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left">
        {SUGGESTED_QUERIES.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              onClick={() => onSelectPrompt(item.prompt)}
              className="p-3.5 rounded-xl border border-zinc-850 hover:border-zinc-700 bg-zinc-900/50 hover:bg-zinc-900 transition-all text-left group flex items-start gap-3 focus:outline-none focus:ring-1 focus:ring-indigo-500/50"
            >
              <div className="p-2 rounded-lg bg-zinc-800 text-zinc-400 group-hover:text-indigo-400 group-hover:bg-indigo-500/10 transition-colors shrink-0">
                <Icon className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <h3 className="text-xs font-semibold text-zinc-200 group-hover:text-indigo-300 transition-colors">
                  {item.title}
                </h3>
                <p className="text-[11px] text-zinc-400 line-clamp-2 mt-0.5 leading-relaxed">
                  {item.desc}
                </p>
              </div>
            </button>
          );
        })}
      </div>

    </div>
  );
}

