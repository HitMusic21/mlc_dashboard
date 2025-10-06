import { useState, useCallback } from 'react';
import { apiClient } from '../services/api';
import type { CatalogUploadResponse } from '../types/catalog';

export interface UploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
  uploadedFile: File | null;
  uploadResult: CatalogUploadResponse | null;
}

export interface UseFileUploadReturn extends UploadState {
  uploadFile: (file: File, publisherName: string) => Promise<CatalogUploadResponse | null>;
  reset: () => void;
}

export function useFileUpload(): UseFileUploadReturn {
  const [state, setState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
    error: null,
    uploadedFile: null,
    uploadResult: null,
  });

  const uploadFile = useCallback(
    async (file: File, publisherName: string): Promise<CatalogUploadResponse | null> => {
      setState({
        isUploading: true,
        progress: 0,
        error: null,
        uploadedFile: file,
        uploadResult: null,
      });

      try {
        // Simulate upload progress (in real implementation, use XHR with progress events)
        const progressInterval = setInterval(() => {
          setState((prev) => ({
            ...prev,
            progress: Math.min(prev.progress + 10, 90),
          }));
        }, 200);

        const result = await apiClient.uploadCatalog(file, publisherName);

        clearInterval(progressInterval);

        setState({
          isUploading: false,
          progress: 100,
          error: null,
          uploadedFile: file,
          uploadResult: result,
        });

        return result;
      } catch (error: any) {
        const errorMessage =
          error.response?.data?.detail ||
          error.message ||
          'Upload failed. Please try again.';

        setState({
          isUploading: false,
          progress: 0,
          error: errorMessage,
          uploadedFile: file,
          uploadResult: null,
        });

        return null;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({
      isUploading: false,
      progress: 0,
      error: null,
      uploadedFile: null,
      uploadResult: null,
    });
  }, []);

  return {
    ...state,
    uploadFile,
    reset,
  };
}
