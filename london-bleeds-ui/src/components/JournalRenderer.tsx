import React from 'react';

// Helper to parse **Bold**, *Italic*, and ***Bold Italic*** inline text
const parseInlineMarkdown = (text: string) => {
  const parts = text.split(/(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*|_.*?_)/g);
  
  return parts.map((part, j) => {
    if (part.startsWith('***') && part.endsWith('***') && part.length >= 6) {
      return <span key={j} className="font-bold italic text-[#CD7B00]">{part.slice(3, -3)}</span>;
    }
    if (part.startsWith('**') && part.endsWith('**') && part.length >= 4) {
      return <span key={j} className="font-bold text-[#CD7B00]">{part.slice(2, -2)}</span>;
    }
    if (part.startsWith('*') && part.endsWith('*') && part.length >= 2) {
      return <span key={j} className="italic">{part.slice(1, -1)}</span>;
    }
    if (part.startsWith('_') && part.endsWith('_') && part.length >= 2) {
      return <span key={j} className="italic">{part.slice(1, -1)}</span>;
    }
    return <span key={j}>{part}</span>;
  });
};

interface JournalRendererProps {
  text?: string;
}

// Renders the Journal in the sidebar
export const JournalRenderer: React.FC<JournalRendererProps> = ({ text = "" }) => {
  const lines = (text || "").split('\n');
  
  return (
    <div className="space-y-3 font-serif text-sm text-[#293351] leading-relaxed">
      {lines.map((line, i) => {
        const trimmed = line.trim();
        if (!trimmed) return null;

        if (trimmed.startsWith('#')) {
            const cleanHeader = trimmed.replace(/^#+\s*/, '');
            return (
                <h4 key={i} className="font-bold text-[#CD7B00] uppercase text-xs tracking-widest mt-5 mb-2 border-b border-[#CD7B00]/20 pb-1">
                    {cleanHeader}
                </h4>
            );
        }

        let content = trimmed;
        let isList = false;

        if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
           isList = true;
           content = trimmed.substring(2);
        }

        if (isList) {
            return (
                <div key={i} className="flex items-start gap-2">
                    <div className="mt-1.5 w-1 min-w-[4px] h-1 rounded-full bg-[#CD7B00] opacity-60" />
                    <p className="leading-relaxed opacity-90">{parseInlineMarkdown(content)}</p>
                </div>
            );
        }

        return <p key={i} className="leading-relaxed opacity-90">{parseInlineMarkdown(content)}</p>;
      })}
    </div>
  );
};

export default JournalRenderer;

