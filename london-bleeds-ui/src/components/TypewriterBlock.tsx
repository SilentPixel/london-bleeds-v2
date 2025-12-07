import React, { useState, useEffect } from 'react';
import { StoryRenderer } from './StoryRenderer';

interface TypewriterBlockProps {
  text?: string;
  onComplete?: () => void;
  scrollToBottom?: () => void;
}

export const TypewriterBlock: React.FC<TypewriterBlockProps> = ({ 
  text = "", 
  onComplete, 
  scrollToBottom 
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(true);
  const timerRef = React.useRef<NodeJS.Timeout | null>(null);

  // Use ref to track previous text to only reset when text actually changes
  const prevTextRef = React.useRef<string | undefined>(undefined);
  const scrollToBottomRef = React.useRef(scrollToBottom);
  const onCompleteRef = React.useRef(onComplete);
  
  // Update refs when props change (but don't trigger effect)
  useEffect(() => {
    scrollToBottomRef.current = scrollToBottom;
    onCompleteRef.current = onComplete;
  }, [scrollToBottom, onComplete]);
  
  useEffect(() => {
    const textValue = text || "";
    
    // Only reset if text content actually changed (not just a re-render)
    // On initial mount, prevTextRef.current will be undefined, so it will run
    // Use strict comparison - undefined !== string, so first render will always run
    // Also check if displayedText is empty (animation hasn't started yet)
    const textChanged = prevTextRef.current !== textValue;
    const needsAnimation = textChanged || displayedText === '';
    
    if (needsAnimation && textValue) {
      // Clear any existing timer to prevent multiple animations
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      
      // Update ref BEFORE starting animation to prevent re-triggering
      prevTextRef.current = textValue;
      
      // Reset displayed text when text prop changes
      setDisplayedText('');
      setIsTyping(true);
      
      const safeText = textValue;
      const chunks = safeText.match(/(\S+\s*|\s+)/g) || [safeText];
      let i = 0;
      const speed = 30; 

      const timer = setInterval(() => {
        if (i < chunks.length) {
          const chunk = chunks[i];
          if (chunk) {
              setDisplayedText(prev => prev + chunk);
          }
          i++;
          scrollToBottomRef.current?.();
        } else {
          clearInterval(timer);
          timerRef.current = null;
          setIsTyping(false);
          onCompleteRef.current?.();
        }
      }, speed);
      
      timerRef.current = timer;

      return () => {
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }
      };
    }
  }, [text]); // Only depend on text

  return (
    <div className="min-h-[40px]"> 
      <StoryRenderer text={displayedText} animate={true} />
      {isTyping && (
        <span className="inline-block w-2 h-4 bg-[#CD7B00] animate-pulse ml-1 align-baseline"/>
      )}
    </div>
  );
};

export default TypewriterBlock;

