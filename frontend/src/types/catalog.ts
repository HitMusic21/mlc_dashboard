/**
 * Catalog upload and match result types
 */

export type UploadStatus = 'uploading' | 'processing' | 'completed' | 'failed';

export type FileFormat = 'csv' | 'excel' | 'json' | 'xml';

export type ConfidenceLevel = 'high' | 'medium' | 'low';

export interface CatalogUpload {
  id: number;
  filename: string;
  file_format: FileFormat;
  file_size_bytes: number;
  publisher_name: string;
  status: UploadStatus;
  progress_percentage: number;
  status_message?: string;
  tracks_count?: number;
  matches_count?: number;
  processing_stats?: {
    total_tracks: number;
    total_matches: number;
    high_confidence_matches: number;
    medium_confidence_matches: number;
    low_confidence_matches: number;
    processing_time_seconds: number;
    throughput: number;
  };
  estimated_time_remaining_seconds?: number;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface UploadedTrack {
  title: string;
  artist?: string;
  composer?: string;
  writer?: string;
  duration?: number;
  iswc?: string;
  year?: number;
  [key: string]: any;
}

export interface CatalogMatch {
  id: number;
  upload_id: number;
  work_id: number;
  uploaded_track_title: string;
  uploaded_track_artist?: string;
  uploaded_track_composer?: string;
  uploaded_track_duration?: number;
  uploaded_track_iswc?: string;
  uploaded_track_year?: number;
  match_score: number;
  confidence_level: ConfidenceLevel;
  rank: number;
  algorithm_used: string;
  matched_work: {
    id: number;
    title: string;
    alternate_titles?: string[];
    iswc?: string;
    contributors?: Array<{
      name: string;
      role: string;
      ipi?: string;
    }>;
    lyrics_languages?: string[];
    country_of_production?: string;
    has_disputed_rights: boolean;
  };
  created_at: string;
}

export interface MatchResultGroup {
  uploaded_track: UploadedTrack;
  matches: CatalogMatch[];
}

export interface CatalogUploadResponse {
  id: number;
  filename: string;
  file_format: FileFormat;
  file_size_bytes: number;
  publisher_name: string;
  status: UploadStatus;
  progress_percentage: number;
  user_id: number;
  created_at: string;
}

export interface CatalogUploadStatusResponse extends CatalogUploadResponse {
  status_message?: string;
  estimated_time_remaining_seconds?: number;
  processing_stats?: any;
}

export interface CatalogResultsResponse {
  data: MatchResultGroup[];
  pagination: {
    page: number;
    limit: number;
    total_items: number;
    total_pages: number;
  };
}

export interface CatalogUploadsListResponse {
  data: CatalogUpload[];
  pagination: {
    page: number;
    limit: number;
    total_items: number;
    total_pages: number;
  };
}
