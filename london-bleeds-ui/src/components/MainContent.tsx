import React, { useRef, useEffect, useState } from 'react';
import { Menu, Send, Lightbulb, Feather, ChevronDown } from 'lucide-react';
import { StoryRenderer } from './StoryRenderer';
import { TypewriterBlock } from './TypewriterBlock';
import type { HistoryMessage } from '../utils/saveLoad';

interface MainContentProps {
  history: HistoryMessage[];
  input: string;
  isLoading: boolean;
  isConsultingHolmes: boolean;
  onInputChange: (value: string) => void;
  onSubmit: (command: string, e?: React.FormEvent) => void;
  onConsultHolmes: () => void;
  onOpenSidebar: () => void;
}

export const MainContent: React.FC<MainContentProps> = ({
  history,
  input,
  isLoading,
  isConsultingHolmes,
  onInputChange,
  onSubmit,
  onConsultHolmes,
  onOpenSidebar
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const isSubmittingRef = useRef<boolean>(false);
  const lastSubmittedValueRef = useRef<string>('');
  const previousLoadingRef = useRef<boolean>(isLoading);
  const [showScrollButton, setShowScrollButton] = useState(false);

  // Memoize scrollToBottom to prevent TypewriterBlock from resetting on every render
  const scrollToBottom = React.useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, []);

  // Track previous history length to only scroll when history actually changes
  const prevHistoryLengthRef = useRef(history.length);
  useEffect(() => {
    if (prevHistoryLengthRef.current !== history.length) {
      prevHistoryLengthRef.current = history.length;
      scrollToBottom();
    }
  }, [history]);

  // Check scroll position to show/hide scroll-to-bottom button
  useEffect(() => {
    const scrollContainer = scrollRef.current;
    if (!scrollContainer) return;

    const checkScrollPosition = () => {
      const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShowScrollButton(!isNearBottom);
    };

    scrollContainer.addEventListener('scroll', checkScrollPosition);
    // Initial check
    checkScrollPosition();

    return () => {
      scrollContainer.removeEventListener('scroll', checkScrollPosition);
    };
  }, [history]);

  // Reset submission refs when loading completes (action finished)
  useEffect(() => {
    // When isLoading changes from true to false, reset submission tracking
    if (previousLoadingRef.current && !isLoading) {
      // Action just completed - reset submission tracking to allow new submissions
      isSubmittingRef.current = false;
      lastSubmittedValueRef.current = '';
    }
    previousLoadingRef.current = isLoading;
  }, [isLoading]);

  return (
    <div 
      className="flex-1 flex flex-col h-full relative max-w-4xl mx-auto w-full"
      onKeyDown={(e) => {
        // Global keyboard handler to prevent accidental form submissions
        // Only allow Enter key submissions when the input is explicitly focused
        if (e.key === 'Enter' && e.target !== inputRef.current && !inputRef.current?.contains(e.target as Node)) {
          e.preventDefault();
          e.stopPropagation();
        }
      }}
      onClick={(e) => {
        // Global click handler to prevent accidental command execution
        // If clicking outside the input area, ensure we don't trigger any submissions
        const target = e.target as HTMLElement;
        const isInputElement = target === inputRef.current || inputRef.current?.contains(target);
        const isButton = target.tagName === 'BUTTON' || target.closest('button');
        
        // If clicking outside the input area, ensure we don't trigger any submissions
        if (!isInputElement && !isButton) {
          // Just prevent any potential form submission from clicks
          e.preventDefault();
          e.stopPropagation();
          // CRITICAL: Blur the input if it has focus to prevent any keyboard events from triggering
          if (inputRef.current && document.activeElement === inputRef.current) {
            inputRef.current.blur();
          }
        }
      }}
    >
      {/* Mobile Menu Button - Floating */}
      <button 
        onClick={onOpenSidebar} 
        className="fixed top-4 left-4 md:hidden z-50 bg-white/90 backdrop-blur-sm border border-[#C5CBDD] rounded-lg p-2 shadow-sm text-[#293351] hover:bg-white transition-colors"
        aria-label="Open sidebar"
      >
        <Menu size={24} />
      </button>

      {/* Scroll-to-Bottom Button */}
      {showScrollButton && (
        <button
          onClick={scrollToBottom}
          className="fixed bottom-24 right-8 z-50 bg-[#293351] text-white rounded-full p-3 shadow-lg hover:bg-[#CD7B00] transition-all flex items-center justify-center"
          aria-label="Scroll to bottom"
        >
          <ChevronDown size={20} />
        </button>
      )}

      {/* Game Feed */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-8 md:px-16 pt-8 pb-32 scroll-smooth"
        onClick={(e) => {
          // Prevent any clicks on the story content from triggering form submission
          // Only allow clicks to focus the input if explicitly clicking on it
          if (e.target !== inputRef.current && !inputRef.current?.contains(e.target as Node)) {
            // Clicking on story content - prevent any form submission
            e.preventDefault();
            e.stopPropagation();
            // CRITICAL: Blur the input if it has focus to prevent any keyboard events from triggering
            if (inputRef.current && document.activeElement === inputRef.current) {
              inputRef.current.blur();
            }
          }
        }}
        onKeyDown={(e) => {
          // Prevent any keyboard events on the story area from triggering submissions
          // Only allow Enter key if the input is focused
          if (e.target !== inputRef.current && !inputRef.current?.contains(e.target as Node)) {
            e.stopPropagation();
            // If Enter is pressed outside the input, prevent any form submission
            if (e.key === 'Enter') {
              e.preventDefault();
            }
          }
        }}
      >
        {history.length === 0 ? (
          <div className="text-[#929DBF] italic">No story content yet...</div>
        ) : (
          history.map((msg, index) => {
            const isAI = msg.role === 'assistant';
            const isLast = index === history.length - 1;

          if (!isAI && msg.role !== 'system') {
            return (
              <div key={`user-${index}`} className="my-8 animate-in slide-in-from-bottom-2 duration-300">
                <div className="pl-4 border-l-[2px] border-[#CD7B00]">
                  <span className="text-[#CD7B00] font-sans text-lg font-medium">
                    {msg.text}
                  </span>
                </div>
              </div>
            );
          }

            // Use a stable key based on index and message content hash to prevent remounting
            const messageKey = `assistant-${index}-${msg.text.length}`;
            
            return (
              <div key={messageKey} className="mb-8">
                {isLast && isAI ? (
                  <TypewriterBlock 
                    key={messageKey} // Stable key prevents remounting
                    text={msg.text} 
                    scrollToBottom={scrollToBottom} 
                  />
                ) : (
                  <StoryRenderer text={msg.text} />
                )}
              </div>
            );
          })
        )}

          {isLoading && (
            <div className="flex items-center gap-2 text-[#CD7B00] my-4 pl-1">
              <Feather size={16} className="animate-bounce" />
              <span className="text-sm italic opacity-70 font-serif">
                {isConsultingHolmes ? "Holmes is deducing..." : "The story continues..."}
              </span>
            </div>
          )}
      </div>

      {/* Input Area */}
      <div className="absolute bottom-0 left-0 right-0 p-8 md:p-16 bg-gradient-to-t from-background via-background to-transparent pointer-events-none">
        <div className="relative pointer-events-auto max-w-3xl mx-auto">
          
          {/* Consult Holmes Button - Moved to float above input */}
          <div className="absolute right-0 -top-10 flex justify-end mb-2 z-20">
             <button
               type="button"
               onClick={(e) => {
                 e.preventDefault();
                 e.stopPropagation();
                 onConsultHolmes();
               }}
               disabled={isLoading}
               className="flex items-center gap-2 bg-[#293351] text-white px-4 py-1.5 rounded-t-lg shadow-sm hover:bg-[#CD7B00] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
             >
               <Lightbulb size={14} className="text-yellow-300" />
               <span className="text-xs font-bold tracking-wide uppercase">Consult Holmes</span>
             </button>
          </div>

          {/* CRITICAL: Wrap input in form to prevent accidental submissions */}
          <form
            onSubmit={(e) => {
              // CRITICAL: Prevent default form submission behavior
              e.preventDefault();
              e.stopPropagation();
              return false;
            }}
            onClick={(e) => {
              e.stopPropagation();
            }}
            onKeyDown={(e) => {
              // Prevent any keyboard events from bubbling up
              if (e.target === inputRef.current) {
                return; // Let input handle its own events
              }
              e.stopPropagation();
            }}
          >
            <input
              ref={inputRef}
              type="text"
              value={input}
              onFocus={(e) => {
                e.stopPropagation();
              }}
              onBlur={(e) => {
                e.stopPropagation();
              }}
              onChange={(e) => {
                // CRITICAL: Only update state, NEVER trigger any submission
                // Completely isolate onChange from any submission logic
                e.stopPropagation();
                if (typeof e.stopImmediatePropagation === 'function') {
                  e.stopImmediatePropagation();
                }
                const newValue = e.target.value;
                // Update state without any side effects
                // Also reset submission tracking when user types (allows resubmission of same command after editing)
                if (newValue !== lastSubmittedValueRef.current) {
                  isSubmittingRef.current = false;
                }
                onInputChange(newValue);
              }}
              onKeyDown={(e) => {
                // Stop all propagation immediately for ALL keys
                e.stopPropagation();
                if (typeof e.stopImmediatePropagation === 'function') {
                  e.stopImmediatePropagation();
                }
                
                // For all non-Enter keys, do nothing except stop propagation
                if (e.key !== 'Enter' || e.shiftKey) {
                  return;
                }
                
                // ONLY handle Enter key when input is actually focused
                // CRITICAL: Only process if the event target is the input itself
                if (e.target !== inputRef.current && !inputRef.current?.contains(e.target as Node)) {
                  return; // Event is not from the input field
                }
                
                e.preventDefault();
                
                // Get current value directly from ref to avoid stale closures
                // Use React state value as source of truth, not DOM value
                const currentValue = (input || inputRef.current?.value || '').trim();
                
                // Multiple guards to prevent duplicate/automatic submission
                if (isSubmittingRef.current) {
                  return; // Already submitting
                }
                if (!currentValue) {
                  return; // Empty input
                }
                if (currentValue === lastSubmittedValueRef.current) {
                  return; // Same command as last submission
                }
                if (isLoading) {
                  return; // Already processing
                }
                
                // All checks passed - submit the command
                lastSubmittedValueRef.current = currentValue;
                isSubmittingRef.current = true;
                
                // CRITICAL: Clear the input field immediately before submission
                // This prevents any possibility of re-submission with the same value
                // Clear both DOM and ensure React state is also cleared via onInputChange
                if (inputRef.current) {
                  inputRef.current.value = '';
                }
                // Also clear React state immediately
                onInputChange('');
                
                // Call onSubmit with explicit command value - NEVER call without a command
                const emptyEvent = { preventDefault: () => {}, stopPropagation: () => {} } as React.FormEvent;
                onSubmit(currentValue, emptyEvent);
                
                // Note: isSubmittingRef will be reset by useEffect when isLoading becomes false
                // This ensures proper cleanup after action completes
              }}
              onKeyPress={(e) => {
                // Prevent any keypress from triggering form submission
                e.stopPropagation();
                if (typeof e.stopImmediatePropagation === 'function') {
                  e.stopImmediatePropagation();
                }
              }}
              onKeyUp={(e) => {
                // Prevent any keyup from triggering form submission
                e.stopPropagation();
                if (typeof e.stopImmediatePropagation === 'function') {
                  e.stopImmediatePropagation();
                }
              }}
              placeholder="What do you wish to do?"
              className="w-full bg-white border border-[#C5CBDD] rounded-lg py-4 pl-6 pr-14 
                         text-[#293351] placeholder-[#929DBF] text-lg focus:outline-none 
                         focus:border-[#CD7B00] focus:ring-1 focus:ring-[#CD7B00] shadow-sm relative z-10"
              autoComplete="off"
              autoFocus={false}
            />
            <button 
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                if (typeof e.stopImmediatePropagation === 'function') {
                  e.stopImmediatePropagation();
                }
                
                // Use React state as source of truth
                const currentValue = (input || inputRef.current?.value || '').trim();
                
                // Guard: Only submit if value has changed and is not empty
                if (!isSubmittingRef.current && currentValue && currentValue !== lastSubmittedValueRef.current && !isLoading) {
                  lastSubmittedValueRef.current = currentValue;
                  isSubmittingRef.current = true;
                  
                  // CRITICAL: Clear the input field immediately before submission
                  // This prevents any possibility of re-submission with the same value
                  if (inputRef.current) {
                    inputRef.current.value = '';
                  }
                  // Also clear React state immediately
                  onInputChange('');
                  
                  // Call onSubmit with explicit command value
                  onSubmit(currentValue, e);
                  // Note: isSubmittingRef will be reset by useEffect when isLoading becomes false
                }
              }}
              disabled={isLoading || !input.trim()}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-[#929DBF] hover:text-[#CD7B00] disabled:opacity-30 transition-colors z-20"
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default MainContent;

