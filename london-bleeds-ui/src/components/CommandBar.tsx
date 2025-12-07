import { useState } from "react";
import { api } from "../api/client";

export default function CommandBar({ onSubmit }: { onSubmit: (scene: string) => void }) {
  const [cmd, setCmd] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!cmd.trim()) return;

    try {
      const res = await api.post("/play", { command: cmd });
      onSubmit(res.data.markdown);
      setCmd("");
    } catch (err: any) {
      console.error("Error sending command", err);
      console.error("Error response:", err?.response);
      console.error("Error response data:", err?.response?.data);
      console.error("Error response text:", err?.response?.text);
      
      let errorMsg = "Unknown error";
      
      // Try to extract error from various possible locations
      if (err?.response) {
        const response = err.response;
        
        // Check response.data (could be object or string)
        if (response.data) {
          if (typeof response.data === 'string') {
            errorMsg = response.data;
          } else if (response.data.detail) {
            errorMsg = response.data.detail;
          } else if (response.data.message) {
            errorMsg = response.data.message;
          } else if (response.data.error) {
            errorMsg = response.data.error;
          }
        }
        
        // If we still don't have a message, use status text
        if (errorMsg === "Unknown error" && response.statusText) {
          errorMsg = response.statusText;
        }
      } else if (err?.message) {
        errorMsg = err.message;
      } else if (err?.code === "ERR_NETWORK" || err?.code === "ECONNREFUSED") {
        errorMsg = "Cannot connect to backend server. Make sure it's running on http://127.0.0.1:8000";
      }
      
      alert(`Error: ${errorMsg}\n\nStatus: ${err?.response?.status || err?.status || 'Unknown'}\n\nCheck the browser console and backend terminal for more details.`);
    }
  }

  return (
    <form 
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        handleSubmit(e);
      }} 
      className="flex gap-2 w-full max-w-[68ch]"
    >
      <input
        className="flex-1 border rounded-lg p-2 text-primary focus:outline-accent"
        value={cmd}
        onChange={(e) => {
          e.stopPropagation();
          setCmd(e.target.value);
        }}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (cmd.trim()) {
              handleSubmit(e);
            }
          }
        }}
        placeholder="Type a command (look, examine diary, talk to Holmes)"
        autoComplete="off"
      />
      <button 
        type="button"
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          if (cmd.trim()) {
            handleSubmit(e);
          }
        }}
        className="bg-accent text-white px-4 py-2 rounded-lg"
      >
        Send
      </button>
    </form>
  );
}

