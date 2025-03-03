import argparse
import time
import os
import zipfile
import requests
from tqdm import tqdm
from collections import Counter

# URL of the ZIP file
ZIP_URL = "https://sjp.pl/sl/odmiany/sjp-odm-20250301.zip"
ZIP_FILE = "sjp-odm-20250301.zip"
EXTRACTED_FILE = "odm.txt"

def download_and_extract():
    """Download and extract odm.txt if it doesn't already exist."""
    if os.path.exists(EXTRACTED_FILE):
        print(f"'{EXTRACTED_FILE}' already exists. Skipping download.")
        return
    
    print(f"Downloading {ZIP_URL}...")
    response = requests.get(ZIP_URL, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    
    with open(ZIP_FILE, "wb") as file, tqdm(
        desc="Downloading",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
            bar.update(len(chunk))

    print("Download complete. Extracting file...")

    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall()
    
    print(f"Extraction complete. Using '{EXTRACTED_FILE}'.")

def find_matching_words(letters):
    """Find words in odm.txt that contain exactly the given letters."""
    unique_words = set()
    required_counts = Counter(letters)
    word_length = len(letters)

    # Start timing execution
    start_time = time.time()

    # Count total lines for progress tracking
    with open(EXTRACTED_FILE, "r") as file:
        lines = file.readlines()
        total_lines = len(lines)

    # Process words from the file
    with open(EXTRACTED_FILE, "r") as file:
        for line in tqdm(file, total=total_lines, desc="Processing Words"):
            words = line.strip().split(",")  # Split words correctly
            for word in words:
                cleaned_word = word.strip().lower()  # Normalize case and trim spaces

                # Check if the word has the exact length and contains only the correct letters
                if len(cleaned_word) == word_length and set(cleaned_word).issubset(set(letters)):
                    word_counts = Counter(cleaned_word)
                    
                    # Ensure exact character counts match
                    if word_counts == required_counts:
                        unique_words.add(cleaned_word)

    # End timer
    end_time = time.time()

    # Print results
    print(f"\nExecution Time: {end_time - start_time:.2f} seconds")
    if unique_words:
        print(f"Matching words ({len(unique_words)} found): {', '.join(sorted(unique_words))}")
    else:
        print("No matching words found.")

def main():
    """Command-line interface for the word finder script."""
    parser = argparse.ArgumentParser(description="Find words in odm.txt that match a given set of letters.")
    parser.add_argument("letters", nargs="?", help="The letters to search for (e.g., 'reneginapi'). If not provided, user will be prompted.")

    args = parser.parse_args()

    # Ensure the dictionary file is available
    download_and_extract()

    # If letters are provided via CLI, use them; otherwise, ask for input
    if args.letters:
        letters = args.letters.strip().lower()
    else:
        letters = input("Enter letters (without spaces, e.g., 'reneginapi'): ").strip().lower()

    find_matching_words(letters)

if __name__ == "__main__":
    main()
