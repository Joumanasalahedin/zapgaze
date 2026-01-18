/**
 * API utility functions for making authenticated requests to the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://20.74.82.26:8000";
const FRONTEND_API_KEY = import.meta.env.VITE_FRONTEND_API_KEY || "";

/**
 * Get the API key from environment variable
 * Falls back to empty string if not set (for development)
 */
export const getApiKey = (): string => {
  return FRONTEND_API_KEY;
};

/**
 * Make an authenticated API call to the backend
 * Automatically includes the API key in headers
 */
export const apiCall = async (url: string, options: RequestInit = {}): Promise<any> => {
  const apiKey = getApiKey();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  // Add API key if available
  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API call failed: ${response.status} ${response.statusText}. ${errorText}`);
    }

    // Handle empty responses
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error("API call error:", error);
    throw error;
  }
};

/**
 * Get the base API URL
 */
export const getApiBaseUrl = (): string => {
  return API_BASE_URL;
};
