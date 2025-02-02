import sqlite3
import paramiko
import csv

# SFTP Connection Details
FTP_HOST = "192.168.1.24"
FTP_PORT = 22
FTP_USER = "user"
FTP_PASSWORD = "DeezNuts"  # Use SSH keys for security if possible
REMOTE_DB_PATH = "/home/user/jellyfin/config/data/library.db"
LOCAL_DB_PATH = "library.db"
OUTPUT_CSV = "movies.csv"  # Combined CSV for movies and TV episodes
OUTPUT_BUMPS_CSV = "bumps.csv"

# Genre to time_slot mapping
GENRE_time_slot_MAP = {
    "Action": "evening",
    "Action & Adventure": "evening",
    "Adult": "evening",
    "Adventure": "afternoon",
    "Animation": "morning",
    "Comedy": "afternoon",
    "Crime": "evening",
    "Documentary": "morning",
    "Drama": "evening",
    "Family": "morning",
    "Fantasy": "afternoon",
    "Game-Show": "morning",
    "History": "afternoon",
    "Horror": "evening",
    "Kids": "morning",
    "Music": "afternoon",
    "Mystery": "evening",
    "Reality": "morning",
    "Romance": "afternoon",
    "Sci-fi & Fantasy": "evening",
    "Science Fiction": "evening",
    "Short": "morning",
    "Sport": "afternoon",
    "TV Movie": "evening",
    "Talk": "morning",
    "Talk-Show": "morning",
    "Thriller": "evening",
    "War": "evening",
    "Western": "evening"
}

def download_database():
    """Downloads the SQLite database file via SFTP."""
    try:
        transport = paramiko.Transport((FTP_HOST, FTP_PORT))
        transport.connect(username=FTP_USER, password=FTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        print("Downloading database...")
        sftp.get(REMOTE_DB_PATH, LOCAL_DB_PATH)
        
        sftp.close()
        transport.close()
        print("Database downloaded successfully!")
    except Exception as e:
        print(f"Error downloading database: {e}")

def convert_ticks_to_minutes(ticks):
    """Converts .NET Ticks (100-nanosecond intervals) to minutes."""
    return ticks / 600_000_000 if ticks else None  # Return None if no valid ticks

def extract_movies_and_tv_episodes_from_db():
    """Extracts movies and TV episodes with valid duration from the SQLite database and saves them as a CSV."""
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()

        # Query: Select movies and TV episodes where 'Path' starts with '/movies' or '/tv/' and RunTimeTicks is NOT NULL
        query = """
        SELECT Name, RunTimeTicks, Genres, Path FROM TypedBaseItems
        WHERE (Path LIKE '/movies%' OR Path LIKE '/tv/%') AND RunTimeTicks IS NOT NULL
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Convert data to list of dictionaries
        combined_data = []
        for row in rows:
            title = row[0]
            duration = convert_ticks_to_minutes(row[1])
            genre = row[2] if row[2] else "Unknown"
            path = row[3]

            # Determine if the entry is a TV episode
            is_tv = path.startswith("/tv/")

            # Only add entries with a valid duration
            if duration is not None:
                # Assign time_slot based on genre, but override to morning if it's a TV episode
                time_slot = GENRE_time_slot_MAP.get(genre, "evening")  # Default to evening if genre is not found in map
                if is_tv:
                    time_slot = "morning"  # Force TV episodes to morning

                combined_data.append({
                    "title": title,
                    "duration": duration,
                    "genre": genre,
                    "time_slot": time_slot,
                    "IsTV": is_tv
                })

        # Save to CSV
        with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["title", "duration", "genre", "time_slot", "IsTV"])
            writer.writeheader()
            writer.writerows(combined_data)

        conn.close()
        print(f"CSV file '{OUTPUT_CSV}' generated successfully with movies and TV episodes!")

    except Exception as e:
        print(f"Error extracting movies and TV episodes: {e}")

def extract_bumps_from_db():
    """Extracts only bumps with valid duration from the SQLite database and saves them as a CSV."""
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()

        # Query: Select only bumps where 'Path' starts with '/bumps' and RunTimeTicks is NOT NULL
        query = """
        SELECT Name, RunTimeTicks FROM TypedBaseItems
        WHERE Path LIKE '/bumps%' AND RunTimeTicks IS NOT NULL
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Convert data to list of dictionaries
        bumps_data = []
        for row in rows:
            title = row[0]
            duration = convert_ticks_to_minutes(row[1])

            # Only add bumps with a valid duration
            if duration is not None:
                bumps_data.append({"title": title, "duration": duration})

        # Save to CSV
        with open(OUTPUT_BUMPS_CSV, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["title", "duration"])
            writer.writeheader()
            writer.writerows(bumps_data)

        conn.close()
        print(f"CSV file '{OUTPUT_BUMPS_CSV}' generated successfully!")

    except Exception as e:
        print(f"Error extracting bumps: {e}")

if __name__ == "__main__":
    download_database()  # Step 1: Download the database
    extract_movies_and_tv_episodes_from_db()  # Step 2: Extract movies and TV episodes with valid duration and save as CSV
    extract_bumps_from_db()  # Step 3: Extract bumps with valid duration and save as CSV