/**
 * Chart Export Utilities
 *
 * Functions for exporting charts as PNG images.
 */

export const exportChartAsPNG = (elementId: string, filename: string = 'chart.png') => {
  const element = document.getElementById(elementId);
  if (!element) {
    console.error(`Element with id "${elementId}" not found`);
    return;
  }

  // Find the SVG element within the chart
  const svg = element.querySelector('svg');
  if (!svg) {
    console.error('SVG element not found');
    return;
  }

  // Get the SVG dimensions
  const svgRect = svg.getBoundingClientRect();
  const canvas = document.createElement('canvas');
  canvas.width = svgRect.width * 2; // 2x for better quality
  canvas.height = svgRect.height * 2;

  const ctx = canvas.getContext('2d');
  if (!ctx) {
    console.error('Could not get canvas context');
    return;
  }

  // Scale for better quality
  ctx.scale(2, 2);

  // Convert SVG to data URL
  const svgString = new XMLSerializer().serializeToString(svg);
  const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(svgBlob);

  const img = new Image();
  img.onload = () => {
    // Fill white background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, svgRect.width, svgRect.height);

    // Draw the image
    ctx.drawImage(img, 0, 0, svgRect.width, svgRect.height);

    // Convert to PNG and download
    canvas.toBlob((blob) => {
      if (blob) {
        const link = document.createElement('a');
        link.download = filename;
        link.href = URL.createObjectURL(blob);
        link.click();
        URL.revokeObjectURL(link.href);
      }
    }, 'image/png');

    URL.revokeObjectURL(url);
  };

  img.onerror = () => {
    console.error('Failed to load SVG image');
    URL.revokeObjectURL(url);
  };

  img.src = url;
};

export const createCSVFromData = (data: any[], filename: string = 'data.csv') => {
  if (!data || data.length === 0) {
    console.error('No data to export');
    return;
  }

  // Get headers from first object
  const headers = Object.keys(data[0]);

  // Create CSV content
  const csvContent = [
    headers.join(','),
    ...data.map(row =>
      headers.map(header => {
        const value = row[header];
        // Escape values containing commas or quotes
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    )
  ].join('\n');

  // Download CSV
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.download = filename;
  link.href = URL.createObjectURL(blob);
  link.click();
  URL.revokeObjectURL(link.href);
};
