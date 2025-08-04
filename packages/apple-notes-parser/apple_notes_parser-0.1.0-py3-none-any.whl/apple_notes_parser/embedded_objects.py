"""Embedded objects extraction for Apple Notes."""

from __future__ import annotations

import sqlite3

from .exceptions import DatabaseError


class EmbeddedObjectExtractor:
    """Extracts embedded objects (hashtags, mentions, etc.) from Apple Notes database."""

    # UTI constants for different embedded object types
    UTI_HASHTAG = "com.apple.notes.inlinetextattachment.hashtag"
    UTI_MENTION = "com.apple.notes.inlinetextattachment.mention"
    UTI_LINK = "com.apple.notes.inlinetextattachment.link"

    def __init__(self, connection: sqlite3.Connection, macos_version: int):
        """Initialize with database connection and macOS version.

        Args:
            connection: Active SQLite database connection.
            macos_version: Detected macOS version for schema compatibility.
        """
        self.connection = connection
        self.macos_version = macos_version

    def get_embedded_objects_for_note(self, note_id: int) -> dict[str, list[str]]:
        """Get all embedded objects for a specific note.

        Retrieves hashtags, mentions, and links that are stored as embedded
        objects in the database. This method is more accurate than regex
        extraction for macOS 11+ databases.

        Args:
            note_id: Database ID of the note to search for embedded objects.

        Returns:
            dict[str, list[str]]: Dictionary with keys 'hashtags', 'mentions', and 'links',
                                 each containing a list of unique strings found.

        Raises:
            DatabaseError: If database query fails.
        """
        if self.macos_version < 11:
            # Hashtags and mentions were added in macOS 11
            return {"hashtags": [], "mentions": [], "links": []}

        try:
            cursor = self.connection.cursor()

            # Query for embedded objects
            # The relationship varies by iOS version - try multiple fields
            # ZNOTE1 seems to be used for hashtags in newer versions
            query = """
            SELECT
                obj.ZTYPEUTI1,
                obj.ZALTTEXT,
                obj.ZTOKENCONTENTIDENTIFIER
            FROM ZICCLOUDSYNCINGOBJECT obj
            WHERE (obj.ZNOTE = ? OR obj.ZNOTE1 = ? OR obj.ZATTACHMENT = ?)
                AND obj.ZTYPEUTI1 IS NOT NULL
                AND obj.ZTYPEUTI1 IN (?, ?, ?)
            """

            cursor.execute(
                query,
                [
                    note_id,
                    note_id,
                    note_id,  # Try multiple relationship fields
                    self.UTI_HASHTAG,
                    self.UTI_MENTION,
                    self.UTI_LINK,
                ],
            )

            hashtags = []
            mentions = []
            links = []

            for row in cursor.fetchall():
                uti = row[0]
                alt_text = row[1]
                token_identifier = row[2]

                if uti == self.UTI_HASHTAG and alt_text:
                    # Hashtag text is in alt_text, remove # if present
                    tag = alt_text.lstrip("#")
                    if tag:
                        hashtags.append(tag)

                elif uti == self.UTI_MENTION and alt_text:
                    # Mention text is in alt_text, remove @ if present
                    mention = alt_text.lstrip("@")
                    if mention:
                        mentions.append(mention)

                elif uti == self.UTI_LINK and (alt_text or token_identifier):
                    # Link could be in either field
                    link = alt_text or token_identifier
                    if link and link.startswith(("http://", "https://")):
                        links.append(link)

            return {
                "hashtags": list(set(hashtags)),  # Remove duplicates
                "mentions": list(set(mentions)),
                "links": list(set(links)),
            }

        except sqlite3.Error as e:
            raise DatabaseError(
                f"Failed to extract embedded objects for note {note_id}: {e}"
            )

    def get_all_hashtags(self) -> list[str]:
        """Get all unique hashtags across all notes.

        Retrieves all hashtags stored as embedded objects in the database.
        Only available for macOS 12+ databases.

        Returns:
            list[str]: Sorted list of all unique hashtags (without # symbol).
                      Empty list for macOS versions below 12.

        Raises:
            DatabaseError: If database query fails.
        """
        if self.macos_version < 12:
            return []

        try:
            cursor = self.connection.cursor()

            query = """
            SELECT DISTINCT ZALTTEXT
            FROM ZICCLOUDSYNCINGOBJECT
            WHERE ZTYPEUTI1 = ?
                AND ZALTTEXT IS NOT NULL
            """

            cursor.execute(query, [self.UTI_HASHTAG])

            hashtags = []
            for row in cursor.fetchall():
                alt_text = row[0]
                if alt_text:
                    tag = alt_text.lstrip("#")
                    if tag:
                        hashtags.append(tag)

            return sorted(set(hashtags))

        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get all hashtags: {e}")

    def get_all_mentions(self) -> list[str]:
        """Get all unique mentions across all notes.

        Retrieves all mentions stored as embedded objects in the database.
        Only available for macOS 12+ databases.

        Returns:
            list[str]: Sorted list of all unique mentions (without @ symbol).
                      Empty list for macOS versions below 12.

        Raises:
            DatabaseError: If database query fails.
        """
        if self.macos_version < 12:
            return []

        try:
            cursor = self.connection.cursor()

            query = """
            SELECT DISTINCT ZALTTEXT
            FROM ZICCLOUDSYNCINGOBJECT
            WHERE ZTYPEUTI1 = ?
                AND ZALTTEXT IS NOT NULL
            """

            cursor.execute(query, [self.UTI_MENTION])

            mentions = []
            for row in cursor.fetchall():
                alt_text = row[0]
                if alt_text:
                    mention = alt_text.lstrip("@")
                    if mention:
                        mentions.append(mention)

            return sorted(set(mentions))

        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get all mentions: {e}")

    def get_notes_with_hashtag(self, hashtag: str) -> list[int]:
        """Get all note IDs that have a specific hashtag.

        Searches for notes containing the specified hashtag in embedded objects.
        Only available for macOS 12+ databases.

        Args:
            hashtag: Hashtag to search for (with or without # symbol).

        Returns:
            list[int]: List of note IDs containing the specified hashtag.
                      Empty list for macOS versions below 12.

        Raises:
            DatabaseError: If database query fails.
        """
        if self.macos_version < 12:
            return []

        try:
            cursor = self.connection.cursor()

            # Look for hashtag with or without # prefix
            hashtag_patterns = [hashtag, f"#{hashtag}"]

            query = """
            SELECT DISTINCT COALESCE(ZNOTE, ZNOTE1, ZATTACHMENT) as note_id
            FROM ZICCLOUDSYNCINGOBJECT
            WHERE ZTYPEUTI1 = ?
                AND ZALTTEXT IN (?, ?)
                AND (ZNOTE IS NOT NULL OR ZNOTE1 IS NOT NULL OR ZATTACHMENT IS NOT NULL)
            """

            cursor.execute(query, [self.UTI_HASHTAG] + hashtag_patterns)

            return [row[0] for row in cursor.fetchall()]

        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get notes with hashtag '{hashtag}': {e}")

    def get_hashtag_counts(self) -> dict[str, int]:
        """Get count of notes for each hashtag.

        Counts how many notes contain each hashtag based on embedded objects.
        Only available for macOS 12+ databases.

        Returns:
            dict[str, int]: Dictionary mapping hashtag names (without # symbol)
                           to the number of notes containing each hashtag.
                           Empty dict for macOS versions below 12.

        Raises:
            DatabaseError: If database query fails.
        """
        if self.macos_version < 12:
            return {}

        try:
            cursor = self.connection.cursor()

            query = """
            SELECT ZALTTEXT, COUNT(DISTINCT COALESCE(ZNOTE, ZNOTE1, ZATTACHMENT)) as note_count
            FROM ZICCLOUDSYNCINGOBJECT
            WHERE ZTYPEUTI1 = ?
                AND ZALTTEXT IS NOT NULL
                AND (ZNOTE IS NOT NULL OR ZNOTE1 IS NOT NULL OR ZATTACHMENT IS NOT NULL)
            GROUP BY ZALTTEXT
            ORDER BY ZALTTEXT
            """

            cursor.execute(query, [self.UTI_HASHTAG])

            hashtag_counts = {}
            for row in cursor.fetchall():
                alt_text = row[0]
                count = row[1]
                if alt_text:
                    tag = alt_text.lstrip("#")
                    if tag:
                        hashtag_counts[tag] = count

            return hashtag_counts

        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get hashtag counts: {e}")
