"""BWARM 2.0 TSV Parser for The MLC Bulk Data Feed.

Parses tab-separated value files from The MLC's BWARM (Bulk Works and Recording Metadata)
data feed. Supports BWARM 2.0 format specification.
"""

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BWARMTSVParser:
    """Parser for BWARM 2.0 TSV format files from The MLC."""

    def __init__(self, data_directory: str):
        """Initialize parser with data directory.

        Args:
            data_directory: Path to directory containing BWARM TSV files
        """
        self.data_directory = Path(data_directory)
        self.manifest: Optional[Dict] = None

    def parse_manifest(self) -> Dict:
        """Parse BWARM manifest file to understand data feed structure.

        Returns:
            Dictionary with manifest metadata and file inventory
        """
        manifest_files = list(self.data_directory.glob("BWARM_Manifest_*.tsv"))

        if not manifest_files:
            raise FileNotFoundError(f"No BWARM manifest file found in {self.data_directory}")

        manifest_file = manifest_files[0]
        logger.info(f"Parsing manifest: {manifest_file.name}")

        with open(manifest_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Parse header section (line 2)
        header_parts = lines[1].strip().split("\t")
        metadata = {
            "data_feed_version_id": header_parts[0],
            "avs_version_id": header_parts[1],
            "data_feed_sender": header_parts[2],
            "data_feed_sender_dpid": header_parts[3],
            "data_feed_recipient": header_parts[4] if len(header_parts) > 4 else None,
            "data_feed_recipient_dpid": header_parts[5] if len(header_parts) > 5 else None,
            "data_feed_created_datetime": header_parts[6] if len(header_parts) > 6 else None,
        }

        # Parse file inventory (lines after line 3)
        files = []
        for line in lines[3:]:
            if line.startswith("EOF"):
                break

            parts = line.strip().split("\t")
            if len(parts) >= 3:
                files.append(
                    {
                        "table_type": parts[0],
                        "file_name": parts[1],
                        "number_of_lines": int(parts[2]) if parts[2] else 0,
                        "md5_hash": parts[3] if len(parts) > 3 else None,
                    }
                )

        self.manifest = {"metadata": metadata, "files": files}
        return self.manifest

    def parse_musical_works(self) -> List[Dict]:
        """Parse musical works TSV file.

        Returns:
            List of musical work dictionaries
        """
        file_path = self.data_directory / "musicalworks.tsv"
        works = []

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")

            for row in reader:
                # Skip comment lines
                if any(row.values()) and not list(row.values())[0].startswith("#"):
                    works.append(
                        {
                            "record_id": row.get("#MusicalWorkRecordId"),
                            "iswc": row.get("ISWC") or None,
                            "title": row.get("MusicalWorkTitle"),
                            "language_code": row.get("LanguageAndScriptCode") or None,
                            "opus_number": row.get("OpusNumber") or None,
                            "composer_catalog_number": row.get("ComposerCatalogNumber") or None,
                            "nominal_duration": row.get("NominalDuration") or None,
                            "has_right_share_in_dispute": (
                                row.get("HasRightShareInDispute", "").upper() == "TRUE"
                            ),
                            "territory_of_public_domain": (
                                row.get("TerritoryOfPublicDomain") or None
                            ),
                            "is_arrangement_of_traditional_work": (
                                row.get("IsArrangementOfTraditionalWork", "").upper() == "TRUE"
                            ),
                            "alternative_work_id_for_us_reversion": (
                                row.get("AlternativeMusicalWorkIdForUsStatutoryReversion") or None
                            ),
                            "us_statutory_reversion_date": (
                                row.get("UsStatutoryReversionDate") or None
                            ),
                            "is_composite_musical_work": (
                                row.get("IsCompositeMusicalWork", "").upper() == "TRUE"
                            ),
                        }
                    )

        logger.info(f"Parsed {len(works)} musical works")
        return works

    def parse_musical_work_identifiers(self) -> List[Dict]:
        """Parse musical work identifiers (proprietary IDs).

        Returns:
            List of identifier dictionaries
        """
        file_path = self.data_directory / "musicalworkidentifiers.tsv"
        identifiers = []

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")

            for row in reader:
                if any(row.values()) and not list(row.values())[0].startswith("#"):
                    identifiers.append(
                        {
                            "record_id": row.get("#ProprietaryMusicalWorkIdentifierRecordId"),
                            "musical_work_record_id": row.get("MusicalWorkRecordId"),
                            "proprietary_id": row.get("ProprietaryId"),
                            "allocating_party_record_id": row.get("AllocatingPartyRecordId"),
                        }
                    )

        logger.info(f"Parsed {len(identifiers)} musical work identifiers")
        return identifiers

    def parse_parties(self) -> List[Dict]:
        """Parse parties (publishers, composers, administrators).

        Returns:
            List of party dictionaries
        """
        file_path = self.data_directory / "parties.tsv"
        parties = []

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")

            for row in reader:
                if any(row.values()) and not list(row.values())[0].startswith("#"):
                    parties.append(
                        {
                            "record_id": row.get("#PartyRecordId"),
                            "isni": row.get("ISNI") or None,
                            "ipi_name_number": row.get("IpiNameNumber") or None,
                            "cisac_society_id": row.get("CisacSocietyId") or None,
                            "dpid": row.get("DPID") or None,
                            "full_name": row.get("FullName"),
                            "names_before_key_name": row.get("NamesBeforeKeyName") or None,
                            "key_name": row.get("KeyName") or None,
                            "names_after_key_name": row.get("NamesAfterKeyName") or None,
                            "contact_name": row.get("ContactName") or None,
                            "email_address": row.get("EmailAddress") or None,
                            "phone_number": row.get("PhoneNumber") or None,
                            "postal_address": row.get("PostalAddress") or None,
                            "contact_information_may_not_be_valid": (
                                (row.get("ContactInformationMayNotBeValid") or "").upper() == "TRUE"
                            ),
                        }
                    )

        logger.info(f"Parsed {len(parties)} parties")
        return parties

    def parse_musical_work_right_shares(self) -> List[Dict]:
        """Parse musical work right shares (ownership and administration).

        Returns:
            List of right share dictionaries
        """
        file_path = self.data_directory / "musicalworkrightshares.tsv"
        shares = []

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")

            for row in reader:
                if any(row.values()) and not list(row.values())[0].startswith("#"):
                    shares.append(
                        {
                            "record_id": row.get("#MusicalWorkRightShareRecordId"),
                            "musical_work_record_id": row.get("MusicalWorkRecordId"),
                            "party_record_id": row.get("PartyRecordId"),
                            "party_role": row.get("PartyRole"),
                            "right_share_percentage": (
                                float(row.get("RightSharePercentage"))
                                if row.get("RightSharePercentage")
                                else 0.0
                            ),
                            "right_share_type": row.get("RightShareType") or None,
                            "rights_type": row.get("RightsType") or None,
                            "validity_start_date": row.get("ValidityStartDate") or None,
                            "validity_end_date": row.get("ValidityEndDate") or None,
                            "preceding_right_share_record_id": (
                                row.get("PrecedingMusicalWorkRightShareRecordId") or None
                            ),
                            "territory_code": row.get("TerritoryCode") or None,
                            "use_type": row.get("UseType") or None,
                        }
                    )

        logger.info(f"Parsed {len(shares)} musical work right shares")
        return shares

    def parse_alternative_musical_work_titles(self) -> List[Dict]:
        """Parse alternative titles for musical works.

        Returns:
            List of alternative title dictionaries
        """
        file_path = self.data_directory / "alternativemusicalworktitles.tsv"
        titles = []

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")

            for row in reader:
                if any(row.values()) and not list(row.values())[0].startswith("#"):
                    titles.append(
                        {
                            "record_id": row.get("#AlternativeMusicalWorkTitleRecordId"),
                            "musical_work_record_id": row.get("MusicalWorkRecordId"),
                            "alternative_title": row.get("AlternativeTitle"),
                            "language_code": row.get("LanguageAndScriptCode") or None,
                            "alternative_title_type": row.get("AlternativeTitleType") or None,
                        }
                    )

        logger.info(f"Parsed {len(titles)} alternative musical work titles")
        return titles

    def parse_all(self) -> Dict[str, List[Dict]]:
        """Parse all BWARM TSV files in the data directory.

        Returns:
            Dictionary with all parsed data organized by entity type
        """
        logger.info(f"Starting BWARM data parsing from {self.data_directory}")

        # Parse manifest first
        manifest = self.parse_manifest()

        # Parse all data files
        data = {
            "manifest": manifest,
            "musical_works": self.parse_musical_works(),
            "musical_work_identifiers": self.parse_musical_work_identifiers(),
            "parties": self.parse_parties(),
            "musical_work_right_shares": self.parse_musical_work_right_shares(),
            "alternative_musical_work_titles": self.parse_alternative_musical_work_titles(),
        }

        # Summary
        total_records = sum(
            len(v) for k, v in data.items() if isinstance(v, list) and k != "manifest"
        )
        logger.info(f"Completed parsing {total_records} total records from BWARM data feed")

        return data
