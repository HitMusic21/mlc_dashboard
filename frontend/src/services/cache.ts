/**
 * Client-side cache service using localStorage.
 * Provides TTL management and type-safe storage.
 */

interface CacheItem<T> {
  value: T;
  expiresAt: number;
}

export class CacheService {
  private prefix: string;

  constructor(prefix = 'bwarm_') {
    this.prefix = prefix;
  }

  /**
   * Generate cache key with namespace prefix
   */
  private makeKey(namespace: string, key: string): string {
    return `${this.prefix}${namespace}:${key}`;
  }

  /**
   * Set a value in cache with optional TTL
   * @param namespace - Cache namespace (e.g., 'user', 'query')
   * @param key - Cache key
   * @param value - Value to cache
   * @param ttlSeconds - Time to live in seconds (default: 5 minutes)
   */
  set<T>(namespace: string, key: string, value: T, ttlSeconds = 300): void {
    const cacheKey = this.makeKey(namespace, key);
    const expiresAt = Date.now() + ttlSeconds * 1000;

    const item: CacheItem<T> = {
      value,
      expiresAt,
    };

    try {
      localStorage.setItem(cacheKey, JSON.stringify(item));
    } catch (error) {
      console.error('Failed to set cache item:', error);
      // Handle quota exceeded error by clearing old items
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        this.clearExpired();
        // Try again after clearing
        try {
          localStorage.setItem(cacheKey, JSON.stringify(item));
        } catch {
          console.error('Failed to set cache item after clearing expired items');
        }
      }
    }
  }

  /**
   * Get a value from cache
   * @param namespace - Cache namespace
   * @param key - Cache key
   * @returns Cached value or null if not found or expired
   */
  get<T>(namespace: string, key: string): T | null {
    const cacheKey = this.makeKey(namespace, key);

    try {
      const itemStr = localStorage.getItem(cacheKey);
      if (!itemStr) {
        return null;
      }

      const item: CacheItem<T> = JSON.parse(itemStr);

      // Check if expired
      if (Date.now() > item.expiresAt) {
        this.delete(namespace, key);
        return null;
      }

      return item.value;
    } catch (error) {
      console.error('Failed to get cache item:', error);
      return null;
    }
  }

  /**
   * Delete a specific cache item
   */
  delete(namespace: string, key: string): void {
    const cacheKey = this.makeKey(namespace, key);
    localStorage.removeItem(cacheKey);
  }

  /**
   * Clear all items in a namespace
   */
  clearNamespace(namespace: string): void {
    const namespacePrefix = this.makeKey(namespace, '');

    const keysToRemove: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(namespacePrefix)) {
        keysToRemove.push(key);
      }
    }

    keysToRemove.forEach((key) => localStorage.removeItem(key));
  }

  /**
   * Clear all cache items (all namespaces)
   */
  clearAll(): void {
    const keysToRemove: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.prefix)) {
        keysToRemove.push(key);
      }
    }

    keysToRemove.forEach((key) => localStorage.removeItem(key));
  }

  /**
   * Clear expired items from cache
   */
  clearExpired(): void {
    const now = Date.now();
    const keysToRemove: string[] = [];

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.prefix)) {
        try {
          const itemStr = localStorage.getItem(key);
          if (itemStr) {
            const item: CacheItem<unknown> = JSON.parse(itemStr);
            if (now > item.expiresAt) {
              keysToRemove.push(key);
            }
          }
        } catch {
          // Invalid JSON, remove it
          keysToRemove.push(key);
        }
      }
    }

    keysToRemove.forEach((key) => localStorage.removeItem(key));
  }

  /**
   * Get cache statistics
   */
  getStats(): { totalItems: number; totalSize: number; expiredItems: number } {
    let totalItems = 0;
    let totalSize = 0;
    let expiredItems = 0;
    const now = Date.now();

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.prefix)) {
        totalItems++;

        const itemStr = localStorage.getItem(key);
        if (itemStr) {
          totalSize += itemStr.length;

          try {
            const item: CacheItem<unknown> = JSON.parse(itemStr);
            if (now > item.expiresAt) {
              expiredItems++;
            }
          } catch {
            expiredItems++;
          }
        }
      }
    }

    return { totalItems, totalSize, expiredItems };
  }

  /**
   * Cache user profile
   */
  setUserProfile(profile: any, ttlSeconds = 1800): void {
    this.set('user', 'profile', profile, ttlSeconds);
  }

  getUserProfile(): any | null {
    return this.get('user', 'profile');
  }

  /**
   * Cache query results
   */
  setQueryResult(queryKey: string, result: any, ttlSeconds = 300): void {
    this.set('query', queryKey, result, ttlSeconds);
  }

  getQueryResult(queryKey: string): any | null {
    return this.get('query', queryKey);
  }

  /**
   * Cache dashboard statistics
   */
  setStatistics(stats: any, ttlSeconds = 600): void {
    this.set('stats', 'dashboard', stats, ttlSeconds);
  }

  getStatistics(): any | null {
    return this.get('stats', 'dashboard');
  }
}

// Export singleton instance
export const cacheService = new CacheService();

// Clear expired items on app startup
cacheService.clearExpired();

// Optionally clear expired items periodically (every 5 minutes)
if (typeof window !== 'undefined') {
  setInterval(() => {
    cacheService.clearExpired();
  }, 5 * 60 * 1000);
}
