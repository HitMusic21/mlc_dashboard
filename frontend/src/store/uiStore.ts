import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

interface UIState {
  // Sidebar
  isSidebarOpen: boolean;
  isSidebarCollapsed: boolean;

  // Modals
  activeModal: string | null;
  modalData: any;

  // Toasts
  toasts: Toast[];

  // Theme
  theme: 'light' | 'dark' | 'auto';

  // Actions
  toggleSidebar: () => void;
  setSidebarOpen: (isOpen: boolean) => void;
  collapseSidebar: (isCollapsed: boolean) => void;

  openModal: (modalId: string, data?: any) => void;
  closeModal: () => void;

  showToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;

  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      // Initial state
      isSidebarOpen: true,
      isSidebarCollapsed: false,
      activeModal: null,
      modalData: null,
      toasts: [],
      theme: 'light',

      // Sidebar actions
      toggleSidebar: () => {
        set((state) => ({ isSidebarOpen: !state.isSidebarOpen }));
      },

      setSidebarOpen: (isOpen) => {
        set({ isSidebarOpen: isOpen });
      },

      collapseSidebar: (isCollapsed) => {
        set({ isSidebarCollapsed: isCollapsed });
      },

      // Modal actions
      openModal: (modalId, data = null) => {
        set({
          activeModal: modalId,
          modalData: data,
        });
      },

      closeModal: () => {
        set({
          activeModal: null,
          modalData: null,
        });
      },

      // Toast actions
      showToast: (toast) => {
        const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const newToast: Toast = {
          ...toast,
          id,
          duration: toast.duration ?? 5000,
        };

        set((state) => ({
          toasts: [...state.toasts, newToast],
        }));

        // Auto-remove toast after duration
        if (newToast.duration && newToast.duration > 0) {
          setTimeout(() => {
            get().removeToast(id);
          }, newToast.duration);
        }
      },

      removeToast: (id) => {
        set((state) => ({
          toasts: state.toasts.filter((toast) => toast.id !== id),
        }));
      },

      // Theme actions
      setTheme: (theme) => {
        set({ theme });
        // Apply theme to document
        if (theme === 'dark') {
          document.documentElement.classList.add('dark');
        } else if (theme === 'light') {
          document.documentElement.classList.remove('dark');
        } else {
          // Auto mode - use system preference
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          if (prefersDark) {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
        }
      },
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({
        isSidebarCollapsed: state.isSidebarCollapsed,
        theme: state.theme,
      }),
    }
  )
);

// Helper hooks for specific UI features
export const useSidebar = () => {
  const {
    isSidebarOpen,
    isSidebarCollapsed,
    toggleSidebar,
    setSidebarOpen,
    collapseSidebar,
  } = useUIStore();

  return {
    isOpen: isSidebarOpen,
    isCollapsed: isSidebarCollapsed,
    toggle: toggleSidebar,
    setOpen: setSidebarOpen,
    collapse: collapseSidebar,
  };
};

export const useModal = () => {
  const { activeModal, modalData, openModal, closeModal } = useUIStore();

  return {
    activeModal,
    modalData,
    open: openModal,
    close: closeModal,
    isOpen: (modalId: string) => activeModal === modalId,
  };
};

export const useToast = () => {
  const { toasts, showToast, removeToast } = useUIStore();

  return {
    toasts,
    success: (message: string, duration?: number) =>
      showToast({ type: 'success', message, duration }),
    error: (message: string, duration?: number) =>
      showToast({ type: 'error', message, duration }),
    warning: (message: string, duration?: number) =>
      showToast({ type: 'warning', message, duration }),
    info: (message: string, duration?: number) =>
      showToast({ type: 'info', message, duration }),
    remove: removeToast,
  };
};
