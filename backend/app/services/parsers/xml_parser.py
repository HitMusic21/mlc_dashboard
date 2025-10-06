"""XML parser for catalog files."""

from typing import List

from lxml import etree


class XMLParser:
    """Parser for XML catalog files."""

    def parse(self, file_content: bytes) -> List[dict]:
        """Parse XML file content into list of tracks.

        Supports basic XML structures with track/song elements.

        Example structure:
        <catalog>
            <track>
                <title>Song Name</title>
                <artist>Artist Name</artist>
                <duration>180</duration>
            </track>
        </catalog>

        Args:
            file_content: Raw XML file bytes

        Returns:
            List of track dictionaries

        Raises:
            ValueError: If XML is invalid or missing required elements
        """
        try:
            # Parse XML
            root = etree.fromstring(file_content)

            # Try common track element names
            track_elements = (
                root.findall(".//track")
                or root.findall(".//song")
                or root.findall(".//work")
            )

            if not track_elements:
                raise ValueError(
                    "XML must contain track, song, or work elements"
                )

            # Parse tracks
            tracks = []
            for track_elem in track_elements:
                # Get title (required) - try different element names
                title_elem = (
                    track_elem.find("title")
                    or track_elem.find("name")
                    or track_elem.find("song")
                )

                if title_elem is None or not title_elem.text:
                    continue

                track = {"title": title_elem.text.strip()}

                # Get artist (optional)
                artist_elem = (
                    track_elem.find("artist")
                    or track_elem.find("composer")
                    or track_elem.find("writer")
                )
                if artist_elem is not None and artist_elem.text:
                    track["artist"] = artist_elem.text.strip()

                # Get duration (optional)
                duration_elem = track_elem.find("duration") or track_elem.find(
                    "length"
                )
                if duration_elem is not None and duration_elem.text:
                    try:
                        track["duration"] = int(duration_elem.text.strip())
                    except ValueError:
                        pass

                # Get ISWC (optional)
                iswc_elem = track_elem.find("iswc") or track_elem.find("iswc_code")
                if iswc_elem is not None and iswc_elem.text:
                    track["iswc"] = iswc_elem.text.strip()

                tracks.append(track)

            if not tracks:
                raise ValueError("XML file contains no valid track data")

            return tracks

        except etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing XML: {str(e)}")
