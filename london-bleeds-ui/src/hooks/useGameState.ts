import { useState, useCallback } from 'react';
import { createSaveSlot } from '../api/client';

export interface Disposition {
  [characterName: string]: {
    trust: number;
    annoyance: number;
  };
}

export interface GameState {
  location: string;
  inventory: string[];
  sanity: number;
  disposition: Disposition;
  journalNotes: string;
}

const INITIAL_SANITY = 100;
const INITIAL_DISPOSITION: Disposition = {
  holmes: { trust: 5, annoyance: 0 },
  abberline: { trust: 3, annoyance: 0 },
  greel: { trust: 1, annoyance: 0 }
};

const INITIAL_JOURNAL = "Act I: Mapping the City.\n\n* **Current Objective:** Assist Holmes with the map deduction.\n* **Key Items:** The Diary.";

export const useGameState = (initialLocation: string = '221b_baker_street') => {
  const [location, setLocation] = useState<string>(initialLocation);
  const [inventory, setInventory] = useState<string[]>([]);
  const [sanity, setSanity] = useState<number>(INITIAL_SANITY);
  const [disposition, setDisposition] = useState<Disposition>(INITIAL_DISPOSITION);
  const [journalNotes, setJournalNotes] = useState<string>(INITIAL_JOURNAL);

  // Helper function to normalize item names for comparison (case-insensitive, whitespace-normalized)
  const normalizeItemName = (item: string): string => {
    return item.trim().replace(/\s+/g, ' ').toLowerCase();
  };

  // Helper function to deduplicate an inventory array
  const deduplicateInventory = useCallback((items: string[]): string[] => {
    const seen = new Set<string>();
    const deduplicated: string[] = [];
    
    for (const item of items) {
      const trimmedItem = item.trim();
      if (!trimmedItem) continue; // Skip empty items
      
      const normalized = normalizeItemName(trimmedItem);
      if (!seen.has(normalized)) {
        seen.add(normalized);
        deduplicated.push(trimmedItem);
      }
    }
    
    return deduplicated;
  }, []);

  // Update location
  const updateLocation = useCallback((newLocation: string) => {
    setLocation(newLocation);
  }, []);

  // Update inventory with proper deduplication
  const updateInventory = useCallback((updates: { add?: string[]; remove?: string[] }) => {
    setInventory(prev => {
      let newInv = [...prev];
      
      if (updates.add) {
        // Normalize existing inventory for comparison
        const normalizedExisting = new Set(newInv.map(item => normalizeItemName(item)));
        
        // Only add items that don't already exist (case-insensitive, whitespace-normalized)
        const itemsToAdd: string[] = [];
        
        updates.add.forEach(item => {
          const trimmedItem = item.trim();
          if (!trimmedItem) return; // Skip empty items
          
          const normalizedItem = normalizeItemName(trimmedItem);
          
          // Check if item already exists
          if (!normalizedExisting.has(normalizedItem)) {
            itemsToAdd.push(trimmedItem);
            // Add to set to prevent duplicates within the same update
            normalizedExisting.add(normalizedItem);
          }
        });
        
        if (itemsToAdd.length > 0) {
          newInv = [...newInv, ...itemsToAdd];
        }
      }
      
      if (updates.remove) {
        // Normalize items to remove for case-insensitive matching
        const normalizedToRemove = new Set(updates.remove.map(item => normalizeItemName(item.trim())));
        newInv = newInv.filter(item => {
          const normalizedItem = normalizeItemName(item);
          return !normalizedToRemove.has(normalizedItem);
        });
      }
      
      return newInv;
    });
  }, []);

  // Update sanity
  const updateSanity = useCallback((delta: number) => {
    setSanity(prev => Math.max(0, Math.min(100, prev + delta)));
  }, []);

  // Update disposition
  const updateDisposition = useCallback((updates: Partial<Disposition>) => {
    setDisposition(prev => {
      const next = { ...prev };
      Object.keys(updates).forEach(char => {
        const update = updates[char];
        if (update) {
          if (next[char]) {
            if (update.trust !== undefined) {
              next[char].trust += update.trust;
            }
            if (update.annoyance !== undefined) {
              next[char].annoyance += update.annoyance;
            }
          } else {
            next[char] = { trust: update.trust ?? 0, annoyance: update.annoyance ?? 0 };
          }
        }
      });
      return next;
    });
  }, []);

  // Update journal
  const updateJournal = useCallback((notes: string) => {
    setJournalNotes(notes);
  }, []);

  // Load state from object
  const loadState = useCallback((state: Partial<GameState>, resetJournal: boolean = false) => {
    if (state.location !== undefined) setLocation(state.location);
    if (state.inventory !== undefined) {
      // Deduplicate inventory when loading
      const deduplicated = deduplicateInventory(state.inventory);
      setInventory(deduplicated);
    }
    if (state.sanity !== undefined) setSanity(state.sanity);
    if (state.disposition !== undefined) setDisposition(state.disposition);
    // Only set journalNotes if provided, otherwise reset to initial if resetJournal is true
    if (resetJournal && state.journalNotes === undefined) {
      setJournalNotes(INITIAL_JOURNAL);
    } else if (state.journalNotes !== undefined) {
      setJournalNotes(state.journalNotes);
    }
  }, [deduplicateInventory]);

  // Get current state
  const getState = useCallback((): GameState => {
    return {
      location,
      inventory,
      sanity,
      disposition,
      journalNotes
    };
  }, [location, inventory, sanity, disposition, journalNotes]);

  // Save to backend (async)
  const saveToBackend = useCallback(async (playerId: string, slotName: string = "Auto Save") => {
    try {
      await createSaveSlot(playerId, slotName);
      return true;
    } catch (error) {
      console.error("Failed to save to backend:", error);
      return false;
    }
  }, []);

  return {
    // State
    location,
    inventory,
    sanity,
    disposition,
    journalNotes,
    // Updaters
    updateLocation,
    updateInventory,
    updateSanity,
    updateDisposition,
    updateJournal,
    // Utilities
    loadState,
    getState,
    saveToBackend
  };
};
