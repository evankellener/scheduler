import pandas as pd
import argparse
import random

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

# Read bumps from a CSV file
def read_bumps_from_csv(file_path):
    """
    Read bumps from a CSV file with columns: title, duration.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        list: List of tuples containing bump titles and durations.
    """
    bumps_df = pd.read_csv(f'./{file_path}')
    bumps = list(bumps_df[["title", "duration"]].itertuples(index=False, name=None))
    return bumps

# Generate a schedule for each time slot with bumps interspersed between movies
def create_schedule(df, bumps, target_duration):
    schedules = {"morning": [], "afternoon": [], "evening": []}
    timeslot_durations = {"morning": 0, "afternoon": 0, "evening": 0}
    bump_index = 0

    # Iterate through time slots
    for time_slot in schedules.keys():
        # Filter movies for the current time slot
        time_slot_movies = df[df["time_slot"] == time_slot]

        # Randomly select the first movie for this time slot
        if not time_slot_movies.empty:
            first_movie = time_slot_movies.sample(n=1).iloc[0]
            schedules[time_slot].append((first_movie["title"], first_movie["duration"]))
            timeslot_durations[time_slot] += first_movie["duration"]

            # Remove the selected movie from the DataFrame to avoid duplicates
            time_slot_movies = time_slot_movies.drop(first_movie.name)

        # Add remaining movies and bumps to the schedule
        for _, row in time_slot_movies.iterrows():
            if timeslot_durations[time_slot] + row["duration"] <= target_duration:
                schedules[time_slot].append((row["title"], row["duration"]))
                timeslot_durations[time_slot] += row["duration"]

                # Add a bump after the movie if there's room
                if bump_index < len(bumps):
                    bump_title, bump_duration = bumps[bump_index]
                    if timeslot_durations[time_slot] + bump_duration <= target_duration:
                        schedules[time_slot].append((bump_title, bump_duration))
                        timeslot_durations[time_slot] += bump_duration
                    bump_index += 1

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a movie schedule.")
    parser.add_argument("--movies_file", type=str, default="movies.csv", help="Path to the movies CSV file.")
    parser.add_argument("--bumps_file", type=str, default="bumps.csv", help="Path to the bumps CSV file.")
    args = parser.parse_args()

    # Read the movies and bumps from CSV files
    movies_df = read_movies_from_csv(args.movies_file)
    bumps = read_bumps_from_csv(args.bumps_file)

    # Create schedules for each timeslot
    target_duration = 8 * 60  # 8 hours in minutes
    schedules = create_schedule(movies_df, bumps, target_duration)

    # Print the schedules
    print_schedules(schedules)