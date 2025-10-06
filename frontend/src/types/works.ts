/**
 * Musical works and resources types
 */

export type ResourceType = 'recording' | 'video';

export interface Resource {
  id: number;
  title: string;
  artist: string;
  resource_type: ResourceType;
  isrc?: string;
  duration?: number;
  release_date?: string;
  label?: string;
  created_at: string;
  updated_at: string;
}

export interface Contributor {
  name: string;
  role: string;
  ipi?: string;
}

export interface MusicalWork {
  id: number;
  title: string;
  alternate_titles?: string[];
  iswc?: string;
  contributors?: string;  // From BWARM: comma-separated string (e.g., "OLIVIA PARASHI, SETH G. DUSTIN")
  publisher?: string;     // From BWARM: publisher name (e.g., "EASTBOURNE MUSIC")
  territory?: string;     // From BWARM: territory code (e.g., "US")
  lyrics_languages?: string[];
  country_of_production?: string;
  has_disputed_rights: boolean;
  created_at: string;
  updated_at: string;
}

export interface MusicalWorkDetailed extends MusicalWork {
  resources: Resource[];
}

export interface WorkSearchRequest {
  query: string;
  filters?: {
    has_iswc?: boolean;
    has_disputed_rights?: boolean;
    country_of_production?: string;
  };
  page?: number;
  limit?: number;
}

export interface WorkSearchResult extends MusicalWork {
  search_score: number;
}

export interface Pagination {
  page: number;
  limit: number;
  total_items: number;
  total_pages: number;
}

export interface ResponseMeta {
  response_time_ms: number;
}

export interface WorksListResponse {
  data: MusicalWork[];
  pagination: Pagination;
  meta: ResponseMeta;
}

export interface WorkSearchResponse {
  data: WorkSearchResult[];
  pagination: Pagination;
  meta: ResponseMeta;
}

export interface MonthlyTrend {
  month: string;
  count: number;
}

export interface DashboardStatistics {
  total_works: number;
  works_with_iswc: number;
  works_with_iswc_percentage: number;
  disputed_works: number;
  disputed_works_percentage: number;
  monthly_trend: MonthlyTrend[];
}

export interface DashboardStatisticsResponse extends DashboardStatistics {}

export interface MLCStatistics {
  unmatched_recordings: number;
  unclaimed_shares: number;
  unclaimed_percentage: number;
  low_confidence_matches: number;
  estimated_unclaimed_value: number;
  claims_submitted: number;
  claims_value: number;
}

export interface MLCStatisticsResponse extends MLCStatistics {}
