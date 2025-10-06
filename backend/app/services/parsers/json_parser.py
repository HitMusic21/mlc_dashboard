"""JSON parser for catalog files."""

import json
from typing import List


class JSONParser:
    """Parser for JSON catalog files."""

    def parse(self, file_content: bytes) -> List[dict]:
        """Parse JSON file content into list of tracks.

        Expected JSON structure:
        [
            {"title": "Song Name", "artist": "Artist Name", "duration": 180},
            ...
        ]

        Or with nested tracks array:
        {
            "tracks": [
                {"title": "Song Name", ...},
                ...
            ]
        }

        Args:
            file_content: Raw JSON file bytes

        Returns:
            List of track dictionaries

        Raises:
            ValueError: If JSON is invalid or missing required fields
        """
        try:
            # Decode bytes to string
            content_str = file_content.decode("utf-8")

            # Parse JSON
            data = json.loads(content_str)

            # Handle different JSON structures
            if isinstance(data, list):
                tracks_data = data
            elif isinstance(data, dict) and "tracks" in data:
                tracks_data = data["tracks"]
            else:
                raise ValueError(
                    "JSON must be an array of tracks or an object with 'tracks' array"
                )

            if not isinstance(tracks_data, list):
                raise ValueError("Tracks data must be an array")

            # Parse tracks
            tracks = []
            for item in tracks_data:
                if not isinstance(item, dict):
                    continue

                # Get title (required)
                title = item.get("title") or item.get("song") or item.get("work")
                if not title or not str(title).strip():
                    continue

                track = {"title": str(title).strip()}

                # Get artist (optional)
                artist = (
                    item.get("artist")
                    or item.get("composer")
                    or item.get("writer")
                )
                if artist and str(artist).strip():
                    track["artist"] = str(artist).strip()

                # Get duration (optional)
                duration = item.get("duration") or item.get("length")
                if duration:
                    track["duration"] = int(duration)

                # Get ISWC (optional)
                iswc = item.get("iswc") or item.get("iswc_code")
                if iswc and str(iswc).strip():
                    track["iswc"] = str(iswc).strip()

                tracks.append(track)

            if not tracks:
                raise ValueError("JSON file contains no valid track data")

            return tracks

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing JSON: {str(e)}")
