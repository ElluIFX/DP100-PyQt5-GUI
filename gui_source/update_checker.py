import re
from typing import Optional, Tuple, Union

import requests


def check_for_updates() -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    Check for updates from GitHub releases.

    Returns:
        Tuple containing:
        - success (bool): Whether the check was successful
        - version (str or None): Latest version string (e.g., "V2.0.0")
        - release_notes (str or None): Release notes (only changelog part)
        - update_url (str or None): URL to the update
    """
    try:
        url = "https://api.github.com/repos/ElluIFX/DP100-PyQt5-GUI/releases/latest"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()

        # Extract version from tag name or title
        if "name" in data:
            # Assuming title format like "V2.0.0 Release"
            version_match = re.match(r"(V\d+\.\d+\.\d+)", data["name"])
            if version_match:
                version = version_match.group(1)
            else:
                version = data["name"].split()[0]  # Get first word before space
        else:
            version = data.get("tag_name", "").strip("v")  # Fallback to tag name
            if not version.startswith("V"):
                version = f"V{version}"

        # Get full release notes and update URL
        full_release_notes = data.get("body", "")
        update_url = data.get("html_url", "")

        # Try to extract only the changelog part
        try:
            # Look for changelog section (either in Chinese or English)
            changelog_patterns = [
                r"##\s+改动日志.*?(?=##|$)",  # Chinese pattern
                r"##\s+Changelog.*?(?=##|$)",  # English pattern
                r"##\s+更新日志.*?(?=##|$)",  # Alternative Chinese pattern
                r"##\s+Changes.*?(?=##|$)",  # Alternative English pattern
            ]

            for pattern in changelog_patterns:
                changelog_match = re.search(pattern, full_release_notes, re.DOTALL)
                if changelog_match:
                    release_notes = changelog_match.group(0).strip()
                    break
            else:
                # If no pattern matched, return the full notes
                release_notes = full_release_notes
        except Exception:
            # If extraction fails, return the full notes
            release_notes = full_release_notes

        return True, version, release_notes, update_url

    except Exception as e:
        err = f"Error checking for updates: {e}"
        return False, err, err, err


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings in format "V2.0.0"

    Args:
        version1: First version string
        version2: Second version string

    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    # Remove 'V' prefix if present
    v1 = version1.removeprefix("V")
    v2 = version2.removeprefix("V")

    # Split into components and convert to integers
    v1_parts = [int(x) for x in v1.split(".")]
    v2_parts = [int(x) for x in v2.split(".")]

    # Make sure both lists have the same length
    while len(v1_parts) < len(v2_parts):
        v1_parts.append(0)
    while len(v2_parts) < len(v1_parts):
        v2_parts.append(0)

    # Compare each component
    for i in range(len(v1_parts)):
        if v1_parts[i] < v2_parts[i]:
            return -1
        elif v1_parts[i] > v2_parts[i]:
            return 1

    # All components are equal
    return 0


if __name__ == "__main__":
    # Example usage
    success, version, notes, url = check_for_updates()
    if success:
        print(f"Latest version: {version}")
        print(f"Release notes: {notes}")
        print(f"Update URL: {url}")
    else:
        print("Failed to check for updates")

    print(compare_versions("V2.0.0", "V2.0.1"))
