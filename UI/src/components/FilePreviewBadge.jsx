import React from 'react';
import { 
  FileText, 
  FileSpreadsheet, 
  FileImage, 
  FileCode, 
  File as GenericFile, 
  X 
} from 'lucide-react';
import { formatFileSize } from '../services/chatService';

/**
 * Returns an appropriate Lucide icon and color scheme based on file extension
 */
function getFileVisuals(fileName) {
  const ext = fileName.split('.').pop()?.toLowerCase();
  
  if (['pdf'].includes(ext)) {
    return {
      icon: FileText,
      color: 'text-rose-400',
      bgColor: 'bg-rose-500/10',
      borderColor: 'border-rose-500/20',
      badge: 'PDF'
    };
  }
  if (['doc', 'docx', 'txt', 'rtf', 'md'].includes(ext)) {
    return {
      icon: FileText,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20',
      badge: ext.toUpperCase()
    };
  }
  if (['xls', 'xlsx', 'csv'].includes(ext)) {
    return {
      icon: FileSpreadsheet,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20',
      badge: ext.toUpperCase()
    };
  }
  if (['png', 'jpg', 'jpeg', 'webp', 'svg', 'gif'].includes(ext)) {
    return {
      icon: FileImage,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/20',
      badge: 'IMG'
    };
  }
  if (['js', 'jsx', 'ts', 'tsx', 'py', 'json', 'html', 'css'].includes(ext)) {
    return {
      icon: FileCode,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20',
      badge: ext.toUpperCase()
    };
  }

  return {
    icon: GenericFile,
    color: 'text-zinc-400',
    bgColor: 'bg-zinc-800/60',
    borderColor: 'border-zinc-700/50',
    badge: 'DOC'
  };
}

export default function FilePreviewBadge({ file, onRemove, isCompact = false }) {
  const name = file.name || 'Document';
  const size = file.size ? formatFileSize(file.size) : '';
  const visuals = getFileVisuals(name);
  const IconComponent = visuals.icon;

  if (isCompact) {
    return (
      <div 
        className={`inline-flex items-center gap-2 px-2.5 py-1.5 rounded-lg border text-xs font-medium ${visuals.bgColor} ${visuals.borderColor} text-zinc-200 transition-colors`}
        title={`${name} (${size})`}
      >
        <IconComponent className={`w-3.5 h-3.5 ${visuals.color}`} />
        <span className="truncate max-w-[130px]">{name}</span>
        {size && <span className="text-zinc-500 text-[10px]">({size})</span>}
      </div>
    );
  }

  return (
    <div className={`group relative flex items-center gap-2.5 pl-3 pr-2 py-2 rounded-xl border ${visuals.bgColor} ${visuals.borderColor} backdrop-blur-sm shadow-sm transition-all hover:border-zinc-600`}>
      <div className={`p-1.5 rounded-lg ${visuals.bgColor}`}>
        <IconComponent className={`w-4 h-4 ${visuals.color}`} />
      </div>

      <div className="flex flex-col min-w-0 pr-1">
        <span className="text-xs font-medium text-zinc-200 truncate max-w-[160px] sm:max-w-[200px]" title={name}>
          {name}
        </span>
        {size && (
          <span className="text-[10px] text-zinc-400 flex items-center gap-1.5">
            <span className="font-mono">{size}</span>
            <span className="text-[9px] px-1 py-0.2 rounded bg-zinc-800/80 text-zinc-400 border border-zinc-700/40">
              {visuals.badge}
            </span>
          </span>
        )}
      </div>

      {onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="ml-auto p-1 rounded-lg text-zinc-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors focus:outline-none"
          title="Remove attachment"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}

