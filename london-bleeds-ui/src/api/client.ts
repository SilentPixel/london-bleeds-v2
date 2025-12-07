import axios from "axios";

// Use relative URLs to leverage Vite proxy in development
// In production, this would be configured to point to the actual backend URL
export const api = axios.create({ 
  baseURL: import.meta.env.DEV ? "" : "http://127.0.0.1:8000"
});

// Types
export interface LocationOut {
  id: string;
  name: string;
  description?: string;
  atmosphere?: string;
  exits: Array<{ label: string; to: string }>;
  immutable: boolean;
}

export interface CharacterOut {
  id: string;
  name: string;
  bio?: string;
  traits: Record<string, any>;
  last_known_location_id?: string;
  immutable: boolean;
}

export interface ItemOut {
  id: string;
  name: string;
  kind?: string;
  seed_description?: string;
  location_id?: string;
  state: Record<string, any>;
  immutable: boolean;
}

export interface PlayRequest {
  command: string;
  player_id?: string;
  current_location_id?: string;
}

export interface PlayResponse {
  markdown: string;
}

export interface SaveSlotRequest {
  name: string;
}

export interface SaveSlotResponse {
  id: string;
  player_id: string;
  name: string;
  created_at: string;
}

// API Functions
// Location management
export const getLocations = async (): Promise<LocationOut[]> => {
  const response = await api.get<LocationOut[]>("/debug/locations");
  return response.data;
};

export const getCharacters = async (): Promise<CharacterOut[]> => {
  const response = await api.get<CharacterOut[]>("/debug/characters");
  return response.data;
};

export const getItems = async (): Promise<ItemOut[]> => {
  const response = await api.get<ItemOut[]>("/debug/items");
  return response.data;
};

export const playTurn = async (command: string, playerId?: string, currentLocationId?: string): Promise<PlayResponse> => {
  const response = await api.post<PlayResponse>("/play", {
    command,
    player_id: playerId,
    current_location_id: currentLocationId
  } as PlayRequest);
  return response.data;
};

export const createSaveSlot = async (playerId: string, name: string): Promise<SaveSlotResponse> => {
  const response = await api.post<SaveSlotResponse>(`/debug/save/${playerId}`, {
    name
  } as SaveSlotRequest);
  return response.data;
};

export const getSaveSlots = async (playerId: string): Promise<any[]> => {
  const response = await api.get<any[]>(`/debug/save/${playerId}`);
  return response.data;
};

export interface LocationUpsertRequest {
  id: string;
  name: string;
  description?: string;
  atmosphere?: string;
  exits?: Array<{ label: string; to: string }>;
  immutable?: boolean;
}

export const upsertLocation = async (location: LocationUpsertRequest): Promise<LocationOut> => {
  const response = await api.post<LocationOut>("/debug/locations", location);
  return response.data;
};

