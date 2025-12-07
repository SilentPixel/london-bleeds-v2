import type { LocationOut } from '../api/client';

// World location type for frontend
export interface WorldLocation {
  id: string;
  name: string;
  atmosphere: string;
  description: string;
  exits: string[];
  interactables: string[];
}

/**
 * Transform backend LocationOut format to frontend WorldLocation format
 */
export const transformLocation = (location: LocationOut): WorldLocation => {
  // Extract exit IDs from ExitLink format
  const exits = location.exits.map(exit => exit.to);
  
  // For now, we'll use a simple interactables list
  // This could be enhanced to fetch from backend if needed
  const interactables: string[] = [];
  
  return {
    id: location.id,
    name: location.name,
    atmosphere: location.atmosphere || '',
    description: location.description || '',
    exits,
    interactables
  };
};

/**
 * Transform array of backend locations to frontend world data format
 */
export const transformLocationsToWorldData = (locations: LocationOut[]): Record<string, WorldLocation> => {
  const worldData: Record<string, WorldLocation> = {};
  
  locations.forEach(location => {
    worldData[location.id] = transformLocation(location);
  });
  
  return worldData;
};

/**
 * Get location name by ID from world data
 */
export const getLocationName = (locationId: string, worldData: Record<string, WorldLocation>, locationsLoaded: boolean = false): string => {
  // If locations haven't loaded yet, show loading
  if (!locationsLoaded) {
    return "Loading...";
  }
  
  // If locations are loaded but empty, show location ID
  if (!worldData || Object.keys(worldData).length === 0) {
    console.warn("Locations loaded but worldData is empty. Location ID:", locationId);
    return locationId || "Unknown Location";
  }
  
  // If location found in worldData, return its name
  if (worldData[locationId]) {
    return worldData[locationId].name;
  }
  
  // Location not found - log for debugging
  console.error("Location not found in worldData:", locationId, "Available locations:", Object.keys(worldData));
  
  // Don't use fallback formatting - this indicates a data problem
  // Return the location ID so it's clear something is wrong
  return locationId || "Unknown Location";
};

