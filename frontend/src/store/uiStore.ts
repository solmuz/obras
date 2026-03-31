import { create } from 'zustand';

interface UIState {
  sidebarOpen: boolean;
  activeProject: string | null;
  selectedAccessory: string | null;

  // Actions
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setActiveProject: (projectId: string | null) => void;
  setSelectedAccessory: (accessoryId: string | null) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  activeProject: null,
  selectedAccessory: null,

  setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setActiveProject: (projectId: string | null) => set({ activeProject: projectId }),
  setSelectedAccessory: (accessoryId: string | null) => set({ selectedAccessory: accessoryId }),
}));
