// Gemini API client
const GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent";

export interface GeminiResponse {
  candidates?: Array<{
    content?: {
      parts?: Array<{
        text?: string;
      }>;
    };
  }>;
  error?: {
    message?: string;
  };
}

/**
 * Get Gemini API key from environment variable or localStorage
 */
export const getGeminiApiKey = (): string | null => {
  // Check environment variable first (from .env file)
  if (import.meta.env.VITE_GEMINI_API_KEY) {
    return import.meta.env.VITE_GEMINI_API_KEY;
  }
  
  // Fallback to localStorage (for user-set keys)
  const stored = localStorage.getItem('gemini_api_key');
  if (stored) return stored;
  
  return null;
};

/**
 * Set Gemini API key in localStorage
 */
export const setGeminiApiKey = (key: string): void => {
  localStorage.setItem('gemini_api_key', key);
};

/**
 * Call Gemini API
 * @param prompt - The prompt to send
 * @param useJson - Whether to request JSON response format
 * @returns The text response from Gemini
 */
export const callGemini = async (prompt: string, useJson: boolean = true): Promise<string> => {
  const apiKey = getGeminiApiKey();
  
  if (!apiKey) {
    throw new Error("Gemini API key not found. Please set it in the settings.");
  }

  try {
    const response = await fetch(`${GEMINI_API_URL}?key=${apiKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{
          role: "user",
          parts: [{ text: prompt }]
        }],
        generationConfig: useJson ? { responseMimeType: "application/json" } : undefined
      })
    });
    
    const data: GeminiResponse = await response.json();
    
    if (data.error) {
      throw new Error(data.error.message || "Gemini API error");
    }
    
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!text) {
      throw new Error("Empty response from Gemini API");
    }
    
    return text;
  } catch (e) {
    console.error("Gemini API Call Failed:", e);
    if (e instanceof Error) {
      throw e;
    }
    throw new Error("Failed to call Gemini API");
  }
};

