import React from 'react';
import ReactMarkdown from 'react-markdown';

interface StoryRendererProps {
  text?: string;
  animate?: boolean;
}

export const StoryRenderer: React.FC<StoryRendererProps> = ({ 
  text = "",
  animate: _animate = false 
}) => {
  return (
    <article className="prose prose-lg max-w-none text-[#293351] font-sans leading-relaxed">
      <ReactMarkdown>{text}</ReactMarkdown>
    </article>
  );
};

export default StoryRenderer;
