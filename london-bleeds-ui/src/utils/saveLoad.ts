import type { GameState } from '../hooks/useGameState';

export interface HistoryMessage {
  role: 'user' | 'assistant' | 'system';
  text: string;
}

export interface SaveGameData {
  history: HistoryMessage[];
  location: string;
  inventory: string[];
  sanity: number;
  disposition: Record<string, { trust: number; annoyance: number }>;
  journalNotes: string;
  timestamp: string;
}

const SAVE_KEY = 'londonBleedsSave';

/**
 * Save game state to localStorage
 */
export const saveGameToLocalStorage = (data: SaveGameData): boolean => {
  try {
    localStorage.setItem(SAVE_KEY, JSON.stringify(data));
    return true;
  } catch (e) {
    console.error("Save failed", e);
    return false;
  }
};

/**
 * Load game state from localStorage
 */
export const loadGameFromLocalStorage = (): SaveGameData | null => {
  try {
    const savedData = localStorage.getItem(SAVE_KEY);
    if (!savedData) {
      return null;
    }
    return JSON.parse(savedData) as SaveGameData;
  } catch (e) {
    console.error("Load failed", e);
    return null;
  }
};

/**
 * Create save data from current state
 */
export const createSaveData = (
  history: HistoryMessage[],
  gameState: GameState
): SaveGameData => {
  return {
    history,
    location: gameState.location,
    inventory: gameState.inventory,
    sanity: gameState.sanity,
    disposition: gameState.disposition,
    journalNotes: gameState.journalNotes,
    timestamp: new Date().toLocaleString()
  };
};

