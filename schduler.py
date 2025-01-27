import pandas as pd
import random
import argparse

# Read movies from a CSV file
def read_movies_from_csv(file_path):
    """
    Read movies from a CSV file with columns: title, duration, time_slot.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        DataFrame: Pandas DataFrame with movie information.
    """
    return pd.read_csv(f'./{file_path}')

# Generate a schedule for each time slot with ads interspersed between movies
def create_schedule(df, ads, target_duration):
    schedules = {"morning": [], "afternoon": [], "evening": []}
    timeslot_durations = {"morning": 0, "afternoon": 0, "evening": 0}
    ads = list(ads.items())
    ad_index = 0

    # Iterate through time slots
    for time_slot in schedules.keys():
        # Filter movies for the current time slot
        time_slot_movies = df[df["time_slot"] == time_slot]
        for _, row in time_slot_movies.iterrows():
            if timeslot_durations[time_slot] + row["duration"] <= target_duration:
                schedules[time_slot].append((row["title"], row["duration"]))
                timeslot_durations[time_slot] += row["duration"]

                # Add an ad after the movie if there's room
                if ad_index < len(ads):
                    ad, ad_duration = ads[ad_index]
                    if timeslot_durations[time_slot] + ad_duration <= target_duration:
                        schedules[time_slot].append((ad, ad_duration))
                        timeslot_durations[time_slot] += ad_duration
                    ad_index += 1

    return schedules

# Print the final schedules
def print_schedules(schedules):
    print("Final Schedule:")
    total_duration = 0
    for time_slot, items in schedules.items():
        print(f"\n{time_slot.capitalize()}:")
        slot_duration = 0
        for title, duration in items:
            print(f"- {title} ({duration} mins)")
            slot_duration += duration
        print(f"Total for {time_slot.capitalize()}: {slot_duration} mins ({slot_duration // 60} hours and {slot_duration % 60} minutes)")
        total_duration += slot_duration
    print(f"\nTotal Schedule Duration: {total_duration} mins ({total_duration // 60} hours and {total_duration % 60} minutes)")

# Ads dictionary
ads = {
    "Geico Ad": 4,
    "Coca-Cola Ad": 3,
    "Nike Ad": 2,
    "Apple Ad": 5,
    "Samsung Ad": 6,
    "Honda Ad": 4,
    "Pepsi Ad": 3,
    "Doritos Ad": 2,
    "Ford Ad": 5,
    "Amazon Ad": 4
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a movie schedule.")
    parser.add_argument("--file", type=str, required=True, help="Path to the movies CSV file.")
    args = parser.parse_args()

    # Read the movies from a CSV file
    movies_csv_path = args.file
    movies_df = read_movies_from_csv(movies_csv_path)

    # Create schedules for each timeslot
    target_duration = 8 * 60  # 8 hours in minutes
    schedules = create_schedule(movies_df, ads, target_duration)

    # Print the schedules
    print_schedules(schedules)
