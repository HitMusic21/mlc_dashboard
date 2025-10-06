import React from 'react';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  text?: string;
  variant?: 'primary' | 'secondary' | 'white';
  fullScreen?: boolean;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  text,
  variant = 'primary',
  fullScreen = false,
  className = '',
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  const variantClasses = {
    primary: 'text-primary-600',
    secondary: 'text-secondary-600',
    white: 'text-white',
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl',
  };

  const spinner = (
    <div className={`flex flex-col items-center gap-3 ${className}`}>
      <svg
        className={`animate-spin ${sizeClasses[size]} ${variantClasses[variant]}`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      {text && (
        <p className={`${textSizeClasses[size]} ${variantClasses[variant]} m-0`}>
          {text}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-secondary-50 z-50">
        {spinner}
      </div>
    );
  }

  return spinner;
};

export interface PageLoadingProps {
  text?: string;
}

export const PageLoading: React.FC<PageLoadingProps> = ({ text = 'Loading...' }) => {
  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <LoadingSpinner size="lg" text={text} />
    </div>
  );
};

export interface InlineLoadingProps {
  text?: string;
}

export const InlineLoading: React.FC<InlineLoadingProps> = ({ text }) => {
  return (
    <div className="inline-flex items-center gap-2">
      <LoadingSpinner size="sm" />
      {text && <span className="text-sm text-secondary-600">{text}</span>}
    </div>
  );
};
