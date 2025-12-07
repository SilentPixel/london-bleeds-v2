import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { MainContent } from './components/MainContent';
import { Notification } from './components/Notification';
import { useGameState } from './hooks/useGameState';
import { getLocations } from './api/client';
import { transformLocationsToWorldData, getLocationName } from './utils/locationTransform';
import type { WorldLocation } from './utils/locationTransform';
import { callGemini, getGeminiApiKey } from './api/gemini';
import { handleActionGemini, handleActionOpenAIStream, isSimpleAction } from './utils/actionHandler';
import type { AIProvider, ActionResponse } from './utils/actionHandler';
import { saveGameToLocalStorage, loadGameFromLocalStorage, createSaveData } from './utils/saveLoad';
import type { HistoryMessage } from './utils/saveLoad';
import type { Disposition } from './hooks/useGameState';

const THEME = {
  colors: {
    bg: '#FDF9F5',
    primary: '#293351',
    accent: '#CD7B00',
    muted: '#929DBF',
    border: '#C5CBDD',
    paper: '#FDF9F5'
  }
};

const INITIAL_LOCATION = '221b_baker_street';  // Changed from 'scene_1_baker_street'
const INITIAL_INVENTORY = ['The Diary (Warm to touch)', 'Pocket Watch', 'Laudanum Vial'];

export default function App() {
  // Game state
  const gameState = useGameState(INITIAL_LOCATION);
  const [history, setHistory] = useState<HistoryMessage[]>([
    { 
      role: 'assistant', 
      text: "### SCENE 1: A STUDY IN SMOKE\n\n> *The pattern is too deliberate...*\n\nYou stand in 221B Baker Street. It is early morning. **Sherlock Holmes** sits cross-legged on the floor, surrounded by a chaotic map of Whitechapel, red string connecting points like *bloody veins*. You hold **The Diary** in your hand; its cover feels faintly warm.\n\nHolmes murmurs without looking up: \"The sigils match the locations, Watson. Inspect the board.\"" 
    }
  ]);
  
  const [input, setInput] = useState('');
  const inputValueRef = React.useRef<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUpdatingJournal, setIsUpdatingJournal] = useState(false);
  const [isConsultingHolmes, setIsConsultingHolmes] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  
  // World data
  const [worldData, setWorldData] = useState<Record<string, WorldLocation>>({});
  const [locationsLoaded, setLocationsLoaded] = useState(false);
  
  // Player management
  const [playerId] = useState<string>(() => {
    const stored = localStorage.getItem('player_id');
    return stored || 'demo';
  });
  
  // AI Provider selection
  const [aiProvider] = useState<AIProvider>(() => {
    const stored = localStorage.getItem('ai_provider');
    return (stored as AIProvider) || 'openai';
  });

  // Load locations on mount
  useEffect(() => {
    const loadLocations = async () => {
      try {
        const locations = await getLocations();
        console.log("Loaded locations from backend:", locations.length);
        
        if (locations.length === 0) {
          console.warn("No locations found in database. Database may need seeding.");
          setNotification({ 
            message: "No locations found. Database may need seeding.", 
            type: "error" 
          });
          setLocationsLoaded(true);
          return;
        }
        
        const transformed = transformLocationsToWorldData(locations);
        setWorldData(transformed);
        setLocationsLoaded(true);
        
        if (import.meta.env.DEV) {
          console.log("World data transformed:", Object.keys(transformed).length, "locations");
        }
      } catch (error) {
        console.error("Failed to load locations:", error);
        setNotification({ message: "Failed to load locations from backend.", type: "error" });
        setLocationsLoaded(true);
      }
    };
    loadLocations();
  }, []);

  // Check and create missing location after locations are loaded
  useEffect(() => {
    const checkAndCreateLocation = async () => {
      if (!locationsLoaded || Object.keys(worldData).length === 0) return;
      
      const currentLocationId = gameState.location;
      if (!worldData[currentLocationId] && currentLocationId) {
        console.warn("Current location not found in worldData:", currentLocationId);
        // Don't create default locations - they should exist in the database
        // If location is missing, it's a data issue that needs to be fixed in the seed data
        console.error("Location missing from database. Please ensure seed data includes:", currentLocationId);
      }
    };
    
    checkAndCreateLocation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [locationsLoaded, worldData, gameState.location]);

  // Load game from localStorage on mount
  useEffect(() => {
    const saved = loadGameFromLocalStorage();
    if (saved && saved.inventory && saved.inventory.length > 0) {
      setHistory([
        { 
          role: 'assistant', 
          text: "### SCENE 1: A STUDY IN SMOKE\n\n> *The pattern is too deliberate...*\n\nYou stand in 221B Baker Street. It is early morning. **Sherlock Holmes** sits cross-legged on the floor, surrounded by a chaotic map of Whitechapel, red string connecting points like *bloody veins*. You hold **The Diary** in your hand; its cover feels faintly warm.\n\nHolmes murmurs without looking up: \"The sigils match the locations, Watson. Inspect the board.\"" 
        }
      ]);
      // Normalize old location IDs to new ones (migration)
      let normalizedLocation = saved.location;
      if (normalizedLocation === 'scene_1_baker_street') {
        normalizedLocation = '221b_baker_street';
        console.log('Migrated old location ID to new one');
      }
      
      // loadState will deduplicate inventory automatically
      gameState.loadState({
        location: normalizedLocation,
        inventory: saved.inventory,
        sanity: saved.sanity,
        disposition: saved.disposition,
        journalNotes: saved.journalNotes
      });
    } else {
      // Starting a new game - reset journal and add initial inventory
      // Reset journal explicitly
      gameState.loadState({
        location: INITIAL_LOCATION,
        inventory: INITIAL_INVENTORY,
        sanity: 100,
        disposition: {},
        journalNotes: undefined
      }, true); // resetJournal = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Save player ID to localStorage
  useEffect(() => {
    localStorage.setItem('player_id', playerId);
  }, [playerId]);

  // Save AI provider to localStorage
  useEffect(() => {
    localStorage.setItem('ai_provider', aiProvider);
  }, [aiProvider]);

  // Main action handler - ONLY accepts explicit command string, never reads from state/ref
  const handleAction = React.useCallback(async (command: string, e?: React.FormEvent) => {
    e?.preventDefault();
    
    // Guard: Must have explicit command - reject if not provided
    if (!command || typeof command !== 'string' || !command.trim()) {
      console.warn('handleAction called without valid command:', command);
      return;
    }
    
    // Guard: Don't process actions during journal update
    if (isUpdatingJournal) {
      return;
    }
    
    // Guard: Don't process if already loading
    if (isLoading) {
      return;
    }

    const userAction = command.trim();
    
    // Clear input immediately to prevent re-triggering
    // CRITICAL: Clear both state and ref to prevent any stale values
    setInput('');
    inputValueRef.current = '';
    
    // Also clear the input field DOM element directly to ensure it's truly empty
    // This prevents any browser auto-fill or cached values from causing re-submission
    if (typeof document !== 'undefined') {
      const inputElement = document.querySelector('input[type="text"]') as HTMLInputElement;
      if (inputElement && inputElement.value) {
        inputElement.value = '';
      }
    }
    
    setIsLoading(true);

    setHistory(prev => [...prev, { role: 'user' as const, text: userAction }]);

    try {
      let response: ActionResponse;
      const isSimple = isSimpleAction(userAction);
      
      // Hybrid approach: Use Gemini for simple actions, OpenAI streaming for complex actions
      if (isSimple) {
        // Use Gemini for simple actions (fast, single call)
        response = await handleActionGemini(userAction, gameState.location, worldData, gameState.getState());
      } else {
        // Use OpenAI with streaming for complex actions (better quality, streaming)
        let accumulatedText = '';
        
        // Add placeholder message for streaming
        setHistory(prev => [...prev, { role: 'assistant' as const, text: '' }]);
        
        response = await handleActionOpenAIStream(
          userAction, 
          gameState.location, 
          playerId,
          (chunk: string) => {
            // Update UI in real-time as chunks arrive
            accumulatedText += chunk;
            setHistory(prev => {
              const newHistory = [...prev];
              const lastMsg = newHistory[newHistory.length - 1];
              if (lastMsg && lastMsg.role === 'assistant') {
                lastMsg.text = accumulatedText;
              }
              return newHistory;
            });
          }
        );
        
        // Update final text if streaming didn't complete properly
        if (response.markdown && accumulatedText !== response.markdown) {
          setHistory(prev => {
            const newHistory = [...prev];
            const lastMsg = newHistory[newHistory.length - 1];
            if (lastMsg && lastMsg.role === 'assistant') {
              lastMsg.text = response.markdown;
            }
            return newHistory;
          });
        }
      }

      let storyText = response.markdown || "The fog is too thick to see...";
      
      if (typeof storyText === 'string') {
        storyText = storyText.trim();
        if ((storyText.startsWith('"') && storyText.endsWith('"')) || 
            (storyText.startsWith("'") && storyText.endsWith("'"))) {
          storyText = storyText.slice(1, -1);
        }
      }

      // For non-streaming responses, update history normally
      if (isSimple) {
        setHistory(prev => {
          const newHistory: HistoryMessage[] = [...prev, { role: 'assistant' as const, text: storyText }];
          const saveData = createSaveData(newHistory, gameState.getState());
          saveGameToLocalStorage(saveData);
          return newHistory;
        });
      } else {
        // For streaming, history was already updated in real-time, just save current state
        setHistory(prev => {
          const saveData = createSaveData(prev, gameState.getState());
          saveGameToLocalStorage(saveData);
          return prev; // Return unchanged since we already updated during streaming
        });
      }

      // Update game state from response
      // FIX: Only update location if it's actually a movement command and location is different
      if (response.newLocationId && worldData[response.newLocationId]) {
        const currentLocation = gameState.location;
        const newLocationId = response.newLocationId;
        
        // Check if this is a movement command (not just looking/examining)
        const normalizedCommand = userAction.toLowerCase().trim();
        const movementKeywords = ['go', 'walk', 'enter', 'move', 'travel', 'head', 'proceed', 'advance', 'step', 'run', 'leave', 'exit'];
        const nonMovementKeywords = ['look', 'examine', 'inspect', 'check', 'read', 'study', 'observe', 'view', 'see', 'watch', 'gaze', 'search'];
        
        const isMovementCommand = movementKeywords.some(keyword => 
          normalizedCommand.startsWith(keyword + ' ') || normalizedCommand === keyword
        );
        const isNonMovementCommand = nonMovementKeywords.some(keyword => 
          normalizedCommand.startsWith(keyword + ' ') || normalizedCommand === keyword
        );
        
        // Only update location if it's explicitly a movement command AND location is different
        // NEVER update location for non-movement commands (look, examine, etc.)
        if (isNonMovementCommand) {
          // Explicitly block location updates for non-movement commands
          // Do nothing
        } else if (isMovementCommand && newLocationId !== currentLocation) {
          // Only update if it's a movement command AND location is different
          gameState.updateLocation(newLocationId);
        } else if (!isMovementCommand && !isNonMovementCommand && newLocationId !== currentLocation) {
          // For ambiguous commands that aren't explicitly movement or non-movement,
          // only update if location is actually different (default behavior for unknown commands)
          gameState.updateLocation(newLocationId);
        }
      }

      if (response.inventoryUpdate) {
        gameState.updateInventory(response.inventoryUpdate);
      }

      if (response.sanityUpdate !== undefined) {
        gameState.updateSanity(response.sanityUpdate);
      }

      if (response.dispositionUpdate) {
        const fullUpdates: Partial<Disposition> = {};
        Object.keys(response.dispositionUpdate).forEach(char => {
          const update = response.dispositionUpdate![char];
          if (update) {
            fullUpdates[char] = {
              trust: update.trust ?? 0,
              annoyance: update.annoyance ?? 0
            };
          }
        });
        gameState.updateDisposition(fullUpdates);
      }

    } catch (error) {
      console.error(error);
      setHistory(prev => [...prev, { 
        role: 'system' as const, 
        text: "The connection to the engine was lost. Please try again." 
      }]);
      setNotification({ message: "Failed to process action.", type: "error" });
    } finally {
      setIsLoading(false);
      // Clear the last submitted value after action completes to allow resubmission of same command
      // This is handled by the component's lastSubmittedValueRef, but we ensure state is clean
    }
  }, [isUpdatingJournal, isLoading, aiProvider, playerId, gameState.location, gameState, worldData]);

  // Consult Holmes feature
  const handleConsultHolmes = async () => {
    if (isConsultingHolmes || isLoading) return;
    
    const apiKey = getGeminiApiKey();
    if (!apiKey) {
      setNotification({ message: "Please set your Gemini API key first.", type: "error" });
      return;
    }

    setIsConsultingHolmes(true);
    setIsLoading(true);

    try {
      const context = history.slice(-4).map(m => `${m.role}: ${m.text || ""}`).join('\n');
      const currentLocationName = getLocationName(gameState.location, worldData, locationsLoaded);
      
      const prompt = `
        You are Sherlock Holmes. The player (Watson) is asking for a hint.
        Current Context: ${context}
        Current Location: ${currentLocationName}
        Current Sanity: ${gameState.sanity}
        
        Task: Give a short, sharp, brilliant deduction or hint about what to do next. 
        Do NOT solve the whole puzzle. Be cryptic but helpful. 
        Start with "Watson, observe..." or similar.
        Format: Plain text.
      `;
      
      const hint = await callGemini(prompt, false);
      let safeHint = hint || "I cannot deduce anything at the moment, Watson.";
      
      safeHint = safeHint.trim();
      if ((safeHint.startsWith('"') && safeHint.endsWith('"')) || 
          (safeHint.startsWith("'") && safeHint.endsWith("'"))) {
        safeHint = safeHint.slice(1, -1);
      }
      
      setHistory(prev => [...prev, { 
        role: 'assistant' as const, 
        text: `> *Holmes leans in closely...*\n\n**Sherlock Holmes**: ${safeHint}` 
      }]);
      
    } catch (error) {
      console.error("Hint failed", error);
      setNotification({ message: "Failed to consult Holmes.", type: "error" });
    } finally {
      setIsConsultingHolmes(false);
      setIsLoading(false);
    }
  };

  // Update Journal feature - FIX: Ensure it doesn't trigger handleAction
  const handleUpdateJournal = async (e?: React.MouseEvent | React.FormEvent) => {
    // Prevent any event propagation that could trigger form submission
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    // Guard: Don't update if already updating or if a game action is in progress
    if (isUpdatingJournal || isLoading) {
      return;
    }
    
    const apiKey = getGeminiApiKey();
    if (!apiKey) {
      setNotification({ message: "Please set your Gemini API key first.", type: "error" });
      return;
    }

    setIsUpdatingJournal(true);
    
    try {
      // Create a copy of history to avoid any side effects
      const recentHistory = [...history].slice(-10).filter(h => h.role !== 'system').map(h => h.text || "").join('\n');
      
      // Get the actual location name from worldData (single source of truth)
      const currentLocationName = getLocationName(gameState.location, worldData, locationsLoaded);
      
      const prompt = `
        You are Dr. Watson.
        Read the following recent game log:
        ${recentHistory}
        
        Task: Update the journal with a structured summary of the case.
        Format: Markdown list.
        REQUIRED KEYS (Strictly follow this format):
        * **Current Location:** ${currentLocationName}
        * **Characters Present:** [Who is here?]
        * **Key Clue Secured:** [Most important item found?]
        * **Observations Noted:** [Brief summary of recent events]
        * **Immediate Objective:** [What should we do next?]
        * **Mental State:** [Brief note on sanity/mood based on ${gameState.sanity}% stability]
        
        IMPORTANT: 
        - Use the exact location name provided above: "${currentLocationName}"
        - Only provide the journal summary. Do NOT include location descriptions or narrative text.
      `;

      const notes = await callGemini(prompt, false);
      // Only update journal notes, do NOT add to history, do NOT trigger any game actions
      gameState.updateJournal(notes || "No notes available.");
    } catch (error) {
      console.error("Journal update failed", error);
      gameState.updateJournal("Could not update journal.");
      setNotification({ message: "Failed to update journal.", type: "error" });
    } finally {
      setIsUpdatingJournal(false);
    }
  };

  // Save game
  const handleSaveGame = () => {
    const saveData = createSaveData(history, gameState.getState());
    const success = saveGameToLocalStorage(saveData);
    if (success) {
      setNotification({ message: "Game Saved Successfully!", type: "success" });
    } else {
      setNotification({ message: "Failed to save game.", type: "error" });
    }
  };

  // Load game
  const handleLoadGame = () => {
    const saved = loadGameFromLocalStorage();
    if (!saved) {
      setNotification({ message: "No saved game found.", type: "error" });
      return;
    }
    setHistory(saved.history);
    gameState.loadState({
      location: saved.location,
      inventory: saved.inventory,
      sanity: saved.sanity,
      disposition: saved.disposition,
      journalNotes: undefined
    }, true);
    setNotification({ message: `Game Loaded! (${saved.timestamp})`, type: "success" });
  };

  // Memoize location name to prevent unnecessary re-renders on every keystroke
  const currentLocationName = React.useMemo(
    () => getLocationName(gameState.location, worldData, locationsLoaded),
    [gameState.location, worldData, locationsLoaded]
  );

  return (
    <div 
      className="flex h-screen w-full overflow-hidden font-sans selection:bg-accent selection:text-white" 
      style={{ backgroundColor: THEME.colors.bg, color: THEME.colors.primary }}
    >
      
      {/* Google Fonts Import */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,400;0,600;1,400&family=Playfair+Display:wght@400;700&display=swap');
        .font-serif { font-family: 'Playfair Display', serif; }
        .font-sans { font-family: 'Open Sans', sans-serif; }
      `}</style>

      {/* NOTIFICATION TOAST */}
      {notification && (
        <Notification 
          message={notification.message} 
          type={notification.type} 
          onClose={() => setNotification(null)} 
        />
      )}

      {/* SIDEBAR */}
      <Sidebar
        locationName={currentLocationName}
        inventory={gameState.inventory}
        journalNotes={gameState.journalNotes}
        sanity={gameState.sanity}
        isUpdatingJournal={isUpdatingJournal}
        isSidebarOpen={isSidebarOpen}
        onCloseSidebar={() => setIsSidebarOpen(false)}
        onUpdateJournal={handleUpdateJournal}
        onSaveGame={handleSaveGame}
        onLoadGame={handleLoadGame}
      />

      {/* MAIN CONTENT AREA */}
      <MainContent
        history={history}
        input={input}
        isLoading={isLoading}
        isConsultingHolmes={isConsultingHolmes}
        onInputChange={React.useCallback((value: string) => {
          setInput(value);
          inputValueRef.current = value;
        }, [])}
        onSubmit={(command, e) => handleAction(command, e)}
        onConsultHolmes={handleConsultHolmes}
        onOpenSidebar={() => setIsSidebarOpen(true)}
      />
    </div>
  );
}
