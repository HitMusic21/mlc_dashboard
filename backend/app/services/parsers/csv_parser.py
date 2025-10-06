"""CSV parser for catalog files."""

import csv
from io import StringIO
from typing import List


class CSVParser:
    """Parser for CSV catalog files."""

    # Required columns (at least one must be present)
    TITLE_COLUMNS = ["title", "song", "work", "track"]
    ARTIST_COLUMNS = ["artist", "composer", "writer", "contributors"]
    DURATION_COLUMNS = ["duration", "length", "time"]
    ISWC_COLUMNS = ["iswc", "iswc_code"]

    def parse(self, file_content: bytes) -> List[dict]:
        """Parse CSV file content into list of tracks.

        Args:
            file_content: Raw CSV file bytes

        Returns:
            List of track dictionaries

        Raises:
            ValueError: If CSV is invalid or missing required columns
        """
        try:
            # Decode bytes to string (try UTF-8, fallback to latin-1)
            try:
                content_str = file_content.decode("utf-8")
            except UnicodeDecodeError:
                content_str = file_content.decode("latin-1")

            # Parse CSV
            csv_file = StringIO(content_str)
            reader = csv.DictReader(csv_file)

            # Validate headers
            if not reader.fieldnames:
                raise ValueError("CSV file has no headers")

            # Normalize headers to lowercase
            headers_lower = [h.lower().strip() for h in reader.fieldnames]

            # Find column mappings
            title_col = self._find_column(headers_lower, self.TITLE_COLUMNS)
            artist_col = self._find_column(headers_lower, self.ARTIST_COLUMNS)
            duration_col = self._find_column(headers_lower, self.DURATION_COLUMNS)
            iswc_col = self._find_column(headers_lower, self.ISWC_COLUMNS)

            if title_col is None:
                raise ValueError(
                    f"CSV must have a title column (one of: {', '.join(self.TITLE_COLUMNS)})"
                )

            # Parse rows
            tracks = []
            for row_num, row in enumerate(reader, start=2):
                # Get title (required)
                title = row.get(reader.fieldnames[headers_lower.index(title_col)])
                if not title or not title.strip():
                    continue  # Skip empty rows

                track = {"title": title.strip()}

                # Get artist (optional)
                if artist_col:
                    artist = row.get(reader.fieldnames[headers_lower.index(artist_col)])
                    if artist and artist.strip():
                        track["artist"] = artist.strip()

                # Get duration (optional)
                if duration_col:
                    duration_str = row.get(
                        reader.fieldnames[headers_lower.index(duration_col)]
                    )
                    duration = self._parse_duration(duration_str)
                    if duration:
                        track["duration"] = duration

                # Get ISWC (optional)
                if iswc_col:
                    iswc = row.get(reader.fieldnames[headers_lower.index(iswc_col)])
                    if iswc and iswc.strip():
                        track["iswc"] = iswc.strip()

                tracks.append(track)

            if not tracks:
                raise ValueError("CSV file contains no valid track data")

            return tracks

        except csv.Error as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {str(e)}")

    def _find_column(self, headers: List[str], possible_names: List[str]) -> str | None:
        """Find matching column name from possible options.

        Args:
            headers: List of header names (lowercase)
            possible_names: List of possible column names to match

        Returns:
            Matched column name or None
        """
        for header in headers:
            if header in possible_names:
                return header
        return None

    def _parse_duration(self, duration_str: str | None) -> int | None:
        """Parse duration string into seconds.

        Supports formats:
        - 180 (seconds)
        - 3:00 (mm:ss)
        - 1:30:00 (hh:mm:ss)

        Args:
            duration_str: Duration string

        Returns:
            Duration in seconds or None if invalid
        """
        if not duration_str:
            return None

        duration_str = duration_str.strip()

        try:
            # Try parsing as integer (seconds)
            return int(duration_str)
        except ValueError:
            pass

        # Try parsing as time format (mm:ss or hh:mm:ss)
        parts = duration_str.split(":")
        if len(parts) == 2:
            # mm:ss
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        elif len(parts) == 3:
            # hh:mm:ss
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

        return None
