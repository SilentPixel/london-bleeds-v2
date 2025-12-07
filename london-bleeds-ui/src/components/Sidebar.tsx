import React from 'react';
import { MapPin, Briefcase, ScrollText, Save, FolderOpen, User, X, Sparkles, Brain } from 'lucide-react';
import { JournalRenderer } from './JournalRenderer';

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

interface SidebarProps {
  locationName: string;
  inventory: string[];
  journalNotes: string;
  sanity: number;
  isUpdatingJournal: boolean;
  isSidebarOpen: boolean;
  onCloseSidebar: () => void;
  onUpdateJournal: (e?: React.MouseEvent) => void;
  onSaveGame: () => void;
  onLoadGame: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  locationName,
  inventory,
  journalNotes,
  sanity,
  isUpdatingJournal,
  isSidebarOpen,
  onCloseSidebar,
  onUpdateJournal,
  onSaveGame,
  onLoadGame
}) => {
  return (
    <>
      {/* MOBILE SIDEBAR OVERLAY */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-[#293351]/50 z-40 md:hidden" 
          onClick={onCloseSidebar} 
        />
      )}

      {/* SIDEBAR */}
      <div 
        className={`
          fixed md:relative z-50 w-80 h-full border-r p-8 transition-transform duration-300 ease-in-out flex flex-col
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `} 
        style={{ borderColor: THEME.colors.border, backgroundColor: THEME.colors.bg }}
        onClick={(e) => e.stopPropagation()}
      >
        
        <div className="flex justify-between items-center mb-8">
          <button onClick={onCloseSidebar} className="md:hidden text-[#293351]">
            <X size={24} />
          </button>
        </div>

        {/* Location */}
        <div className="mb-8">
           <div className="flex items-center gap-2 text-[#CD7B00] mb-2">
             <MapPin size={18} />
             <span className="uppercase tracking-widest text-xs font-bold">Current Location</span>
           </div>
           <h2 className="font-serif text-2xl leading-tight text-[#293351]">
             {locationName || "Unknown Location"}
           </h2>
        </div>

        {/* Inventory */}
        <div className="mb-8">
          <div className="flex items-center gap-2 text-[#CD7B00] mb-4">
            <Briefcase size={18} />
            <span className="uppercase tracking-widest text-xs font-bold">Inventory</span>
          </div>
          <ul className="space-y-3" onClick={(e) => e.stopPropagation()}>
            {inventory.map((item, idx) => (
              <li key={idx} className="flex items-center gap-3 text-[#293351] opacity-90">
                <div className="w-1.5 h-1.5 rounded-full bg-[#CD7B00]" />
                <span className="font-sans text-md">{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Journal */}
        <div className="flex-1 flex flex-col min-h-0 mb-8">
          <div className="flex items-center justify-between text-[#CD7B00] mb-4">
            <div className="flex items-center gap-2">
              <ScrollText size={18} />
              <span className="uppercase tracking-widest text-xs font-bold">Watson's Journal</span>
            </div>
            <button 
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onUpdateJournal(e);
              }}
              onMouseDown={(e) => {
                // Prevent focus on the input when clicking this button
                e.preventDefault();
                e.stopPropagation();
              }}
              disabled={isUpdatingJournal}
              className="p-1 hover:bg-[#CD7B00]/10 rounded-full transition-colors"
              title="Update Notes with AI"
            >
              <Sparkles size={14} className={isUpdatingJournal ? "animate-spin" : ""} />
            </button>
          </div>
          <div 
            className="bg-white border border-[#C5CBDD] rounded-lg p-4 flex-1 overflow-y-auto shadow-sm relative"
            onClick={(e) => e.stopPropagation()}
          >
             {/* Sanity Indicator (Visual Only - Hidden mechanic) */}
             <div className="absolute top-2 right-2 opacity-30" title={`Mental Stability: ${sanity}%`}>
                <Brain size={16} color={sanity < 50 ? 'red' : '#293351'} />
             </div>
            <JournalRenderer text={journalNotes} />
          </div>
        </div>

        {/* SYSTEM BUTTONS (Save / Load) */}
        <div className="grid grid-cols-2 gap-3">
          <button 
            onClick={onSaveGame}
            className="flex items-center justify-center gap-2 bg-[#293351] text-white p-2 rounded hover:bg-[#CD7B00] transition-colors text-xs font-bold uppercase tracking-wider"
          >
            <Save size={14} /> Save
          </button>
          <button 
            onClick={onLoadGame}
            className="flex items-center justify-center gap-2 border border-[#293351] text-[#293351] p-2 rounded hover:bg-[#293351] hover:text-white transition-colors text-xs font-bold uppercase tracking-wider"
          >
            <FolderOpen size={14} /> Load
          </button>
        </div>

        <div className="mt-6 pt-6 border-t" style={{ borderColor: THEME.colors.border }}>
          <div className="flex items-center gap-3 text-[#293351] opacity-70">
            <User size={18} />
            <span className="font-sans text-sm">Dr. John Watson</span>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
