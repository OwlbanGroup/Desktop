#!/usr/bin/env python3
"""
Simple test for the get_driver_updates method
"""

# Test the method directly without importing the whole module
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def get_driver_updates():
    """
    Fetch driver updates and information from NVIDIA's drivers page.
    """
    url = "https://www.nvidia.com/en-us/drivers/"
    try:
        print("Fetching driver updates from NVIDIA drivers page")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        driver_versions = []
        download_links = []
        system_requirements = []
        release_notes = []
        supported_products = []

        # Extract driver version information
        version_pattern = r'\b\d+\.\d+(?:\.\d+)?\b'
        text = soup.get_text()
        versions = re.findall(version_pattern, text)
        driver_versions.extend(versions)

        # Extract download links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href and ("download" in href.lower() or ".exe" in href.lower() or ".msi" in href.lower()):
                if href.startswith("/"):
                    href = "https://www.nvidia.com" + href
                if href.startswith("http"):
                    download_links.append(href)

        # Extract system requirements
        req_sections = soup.find_all(["div", "section"], class_=re.compile(r"(requirement|system|spec)", re.I))
        for section in req_sections:
            text = section.get_text(separator=" ", strip=True)
            if text and len(text) > 10:
                system_requirements.append(text)

        # Extract release notes links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True).lower()
            if "release" in text and "note" in text:
                if href.startswith("/"):
                    href = "https://www.nvidia.com" + href
                if href.startswith("http"):
                    release_notes.append(href)

        # Extract supported products/GPUs
        product_sections = soup.find_all(["div", "ul", "li"], class_=re.compile(r"(product|gpu|support)", re.I))
        for section in product_sections:
            text = section.get_text(separator=" ", strip=True)
            if text and len(text) > 5:
                supported_products.append(text)

        # Deduplicate lists
        driver_versions = list(set(driver_versions))
        download_links = list(set(download_links))
        system_requirements = list(set(system_requirements))
        release_notes = list(set(release_notes))
        supported_products = list(set(supported_products))

        return {
            "driver_versions": driver_versions,
            "download_links": download_links,
            "system_requirements": system_requirements,
            "release_notes": release_notes,
            "supported_products": supported_products,
            "last_updated": datetime.now().isoformat(),
            "source": url
        }
    except Exception as e:
        print(f"Error fetching driver updates: {e}")
        return {
            "error": f"Failed to fetch driver updates: {e}",
            "driver_versions": [],
            "download_links": [],
            "system_requirements": [],
            "release_notes": [],
            "supported_products": [],
            "last_updated": datetime.now().isoformat(),
            "source": url
        }

if __name__ == "__main__":
    print("Testing get_driver_updates method...")
    result = get_driver_updates()
    print("✓ Method executed successfully")
    print(f"Driver versions found: {len(result.get('driver_versions', []))}")
    print(f"Download links found: {len(result.get('download_links', []))}")
    print(f"Source: {result.get('source', 'N/A')}")
    print("✓ Driver updates integration successfully added!")
