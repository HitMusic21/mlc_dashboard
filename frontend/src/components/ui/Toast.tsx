import React from 'react';
import { useToast } from '../../store/uiStore';

export const ToastContainer: React.FC = () => {
  const { toasts, remove } = useToast();

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          id={toast.id}
          type={toast.type}
          message={toast.message}
          onClose={() => remove(toast.id)}
        />
      ))}
    </div>
  );
};

interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({ type, message, onClose }) => {
  const [isExiting, setIsExiting] = React.useState(false);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      onClose();
    }, 300); // Match animation duration
  };

  const typeStyles = {
    success: {
      bg: 'bg-success-50 border-success-500',
      text: 'text-success-900',
      icon: (
        <svg
          className="w-5 h-5 text-success-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 13l4 4L19 7"
          />
        </svg>
      ),
    },
    error: {
      bg: 'bg-error-50 border-error-500',
      text: 'text-error-900',
      icon: (
        <svg
          className="w-5 h-5 text-error-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      ),
    },
    warning: {
      bg: 'bg-warning-50 border-warning-500',
      text: 'text-warning-900',
      icon: (
        <svg
          className="w-5 h-5 text-warning-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      ),
    },
    info: {
      bg: 'bg-primary-50 border-primary-500',
      text: 'text-primary-900',
      icon: (
        <svg
          className="w-5 h-5 text-primary-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
    },
  };

  const style = typeStyles[type];

  return (
    <div
      className={`
        ${style.bg} ${style.text}
        border-l-4 rounded-lg shadow-lg p-4 min-w-[320px] max-w-md
        flex items-start gap-3 pointer-events-auto
        transition-all duration-300 ease-in-out
        ${isExiting ? 'opacity-0 translate-x-full' : 'opacity-100 translate-x-0'}
      `}
      role="alert"
    >
      <div className="flex-shrink-0">{style.icon}</div>
      <div className="flex-1 pt-0.5">
        <p className="text-sm font-medium m-0">{message}</p>
      </div>
      <button
        onClick={handleClose}
        className="flex-shrink-0 p-1 rounded hover:bg-black hover:bg-opacity-5 transition-colors border-none bg-transparent cursor-pointer"
        aria-label="Close notification"
      >
        <svg
          className="w-4 h-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>
  );
};
