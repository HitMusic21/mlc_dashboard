import { useState, useCallback, useRef } from 'react';

export interface VirtualizationOptions {
  itemHeight: number;
  containerHeight: number;
  itemCount: number;
  overscan?: number;
}

export interface VirtualizationResult {
  visibleStartIndex: number;
  visibleEndIndex: number;
  totalHeight: number;
  offsetY: number;
  scrollToIndex: (index: number) => void;
  handleScroll: (event: React.UIEvent<HTMLElement>) => void;
}

export function useVirtualization({
  itemHeight,
  containerHeight,
  itemCount,
  overscan = 3,
}: VirtualizationOptions): VirtualizationResult {
  const [scrollTop, setScrollTop] = useState(0);
  const scrollElementRef = useRef<HTMLElement | null>(null);

  // Calculate visible range
  const visibleStartIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const visibleEndIndex = Math.min(
    itemCount - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );

  // Total height of all items
  const totalHeight = itemCount * itemHeight;

  // Offset for positioning visible items
  const offsetY = visibleStartIndex * itemHeight;

  // Scroll to specific index
  const scrollToIndex = useCallback(
    (index: number) => {
      if (!scrollElementRef.current) return;

      const targetScroll = index * itemHeight;
      scrollElementRef.current.scrollTop = targetScroll;
    },
    [itemHeight]
  );

  // Handle scroll events
  const handleScroll = useCallback((event: React.UIEvent<HTMLElement>) => {
    const target = event.currentTarget;
    scrollElementRef.current = target;
    setScrollTop(target.scrollTop);
  }, []);

  return {
    visibleStartIndex,
    visibleEndIndex,
    totalHeight,
    offsetY,
    scrollToIndex,
    handleScroll,
  };
}
