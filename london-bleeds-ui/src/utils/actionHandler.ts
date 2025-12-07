import { playTurn } from '../api/client';
import { callGemini } from '../api/gemini';
import { createGameEnginePrompt } from '../prompts/gameEngine';
import type { WorldLocation } from './locationTransform';
import type { Disposition } from '../hooks/useGameState';

export type AIProvider = 'openai' | 'gemini';

/**
 * Determine if an action is simple (use Gemini) or complex (use OpenAI)
 */
export function isSimpleAction(action: string): boolean {
  const normalized = action.toLowerCase().trim();
  
  // Simple actions - basic observation/interaction
  const simpleKeywords = [
    'look', 'examine', 'inspect', 'check', 'read', 'study', 
    'observe', 'view', 'see', 'watch', 'gaze', 'search',
    'take', 'get', 'pick up', 'drop', 'put'
  ];
  
  // Complex actions - require reasoning/deduction
  const complexKeywords = [
    'talk', 'speak', 'say', 'tell', 'ask', 'question',
    'think', 'deduce', 'analyze', 'compare', 'connect',
    'show', 'give', 'present', 'explain', 'why', 'how',
    'consult', 'discuss', 'hypothesize', 'theorize'
  ];
  
  // Check for complex keywords first (higher priority)
  if (complexKeywords.some(keyword => 
    normalized.startsWith(keyword + ' ') || normalized === keyword
  )) {
    return false;
  }
  
  // Check for simple keywords
  if (simpleKeywords.some(keyword => 
    normalized.startsWith(keyword + ' ') || normalized === keyword
  )) {
    return true;
  }
  
  // Default: treat as complex for safety (better quality)
  return false;
}

export interface InventoryUpdate {
  add?: string[];
  remove?: string[];
}

export interface DispositionUpdate {
  [characterName: string]: {
    trust?: number;
    annoyance?: number;
  };
}

export interface ActionResponse {
  markdown: string;
  newLocationId?: string;
  inventoryUpdate?: InventoryUpdate;
  sanityUpdate?: number;
  dispositionUpdate?: DispositionUpdate;
}

interface GeminiGameResponse {
  thoughtProcess?: string;
  markdownOutput: string;
  newLocationId?: string;
  inventoryUpdate?: InventoryUpdate;
  dispositionUpdate?: DispositionUpdate;
  sanityUpdate?: number;
  gameOver?: boolean;
}

/**
 * Handle action using OpenAI backend API
 */
export const handleActionOpenAI = async (
  userAction: string,
  currentLocation: string,
  playerId?: string
): Promise<ActionResponse> => {
  try {
    const response = await playTurn(userAction, playerId, currentLocation);
    
    // Backend API only returns markdown, so we construct a basic response
    // The backend may include location changes in the markdown or through other means
    // For now, we return just the markdown and let the frontend handle location parsing if needed
    return {
      markdown: response.markdown || "The fog is too thick to see...",
    };
  } catch (error) {
    console.error('OpenAI action handler error:', error);
    throw error;
  }
};

/**
 * Handle action using Gemini API directly
 */
export const handleActionGemini = async (
  userAction: string,
  currentLocation: string,
  worldData: Record<string, WorldLocation>,
  gameState: {
    location: string;
    inventory: string[];
    sanity: number;
    disposition: Disposition;
    journalNotes: string;
  }
): Promise<ActionResponse> => {
  try {
    // Build the prompt with game context
    const promptBase = createGameEnginePrompt(worldData);
    
    const fullPrompt = `${promptBase}

CURRENT GAME STATE:
- Location: ${currentLocation}
- Inventory: ${gameState.inventory.join(', ') || 'Empty'}
- Sanity: ${gameState.sanity}
- Disposition: ${JSON.stringify(gameState.disposition)}
- Journal: ${gameState.journalNotes}

PLAYER ACTION: "${userAction}"

Respond with ONLY a valid JSON object following the RESPONSE JSON STRUCTURE above. Do not include any text before or after the JSON.`;

    // Call Gemini API with JSON response format
    const jsonResponse = await callGemini(fullPrompt, true);
    
    // Parse the JSON response
    let parsedResponse: GeminiGameResponse;
    try {
      // Clean up the response in case there's extra text
      const jsonMatch = jsonResponse.match(/\{[\s\S]*\}/);
      const jsonText = jsonMatch ? jsonMatch[0] : jsonResponse;
      parsedResponse = JSON.parse(jsonText);
    } catch (parseError) {
      console.error('Failed to parse Gemini JSON response:', jsonResponse);
      throw new Error('Invalid JSON response from Gemini API');
    }

    // Map Gemini response to ActionResponse format
    return {
      markdown: parsedResponse.markdownOutput || "The fog is too thick to see...",
      newLocationId: parsedResponse.newLocationId,
      inventoryUpdate: parsedResponse.inventoryUpdate,
      sanityUpdate: parsedResponse.sanityUpdate,
      dispositionUpdate: parsedResponse.dispositionUpdate,
    };
  } catch (error) {
    console.error('Gemini action handler error:', error);
    throw error;
  }
};

/**
 * Handle action using OpenAI backend API with streaming
 */
export const handleActionOpenAIStream = async (
  userAction: string,
  currentLocation: string,
  playerId?: string,
  onChunk?: (chunk: string) => void
): Promise<ActionResponse> => {
  try {
    const response = await fetch('/play/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        command: userAction,
        player_id: playerId,
        current_location_id: currentLocation
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullText = '';
    let nextActions: string[] = [];

    if (!reader) {
      throw new Error('No response body');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            
            if (data.type === 'chunk') {
              fullText += data.content;
              if (onChunk) {
                onChunk(data.content);
              }
            } else if (data.type === 'metadata') {
              nextActions = data.next_actions || [];
            } else if (data.type === 'done') {
              // Streaming complete
            } else if (data.type === 'error') {
              throw new Error(data.message);
            }
          } catch (e) {
            // Skip invalid JSON lines
            continue;
          }
        }
      }
    }

    return {
      markdown: fullText.trim() || "The fog is too thick to see...",
    };
  } catch (error) {
    console.error('OpenAI streaming action handler error:', error);
    throw error;
  }
};
