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
    bumps = pd.read_csv(f'./{file_path}')
    return bumps

def create_schedule(movies_df, bumps_df, target_duration):
    schedules = {}
    time_periods = ['morning', 'afternoon', 'evening']
    total_target_time = target_duration  # Maximum schedule time in minutes
    min_time = 450  # Minimum required time
    
    for period in time_periods:
        valid_schedule = False
        
        while not valid_schedule:
            selected_movies = []
            total_time = 0
            remaining_time = total_target_time
            
            # Randomly select movies until reaching the time constraints
            available_movies = movies_df.copy()
            while total_time < min_time:
                if available_movies.empty:
                    break  # Avoid infinite loops if no more movies available
                movie = available_movies.sample(n=1).iloc[0]
                movie_duration = movie['duration']
                if total_time + movie_duration <= total_target_time:
                    selected_movies.append(movie)
                    total_time += movie_duration
                    available_movies = available_movies.drop(movie.name)
                else:
                    break
            
            # Check if the schedule is within the acceptable range
            if min_time <= total_time <= total_target_time:
                valid_schedule = True
        
        # Add bumps to fill up remaining time
        remaining_time = total_target_time - total_time
        bump_schedule = []
        available_bumps = bumps_df.copy()
        
        while remaining_time > 0:
            bump = available_bumps.sample(n=1).iloc[0]
            bump_duration = bump['duration']
            if remaining_time - bump_duration >= 0:
                bump_schedule.append(bump)
                remaining_time -= bump_duration
                available_bumps = available_bumps.drop(bump.name)
            else:
                break
        
        # Combine movies and bumps into final schedule
        schedule = []
        for movie in selected_movies:
            schedule.append(movie['title'])
            if bump_schedule:
                bump = bump_schedule.pop(0)
                schedule.append(bump['title'])
        
        schedules[period] = schedule
    
    return schedules

# Print the final schedules
def print_schedules(schedules, movies_df, bumps_df):
    print("Final Schedule:")
    total_duration = 0
    for time_slot, items in schedules.items():
        print(f"\n{time_slot.capitalize()}:")
        slot_duration = 0
        for title in items:
            # Find the duration of the movie or bump
            duration = movies_df.loc[movies_df["title"] == title, "duration"].values
            if duration.size == 0:  # If not found in movies, search bumps
                duration = bumps_df.loc[bumps_df["title"] == title, "duration"].values
            
            duration = duration[0] if duration.size > 0 else 0  # Ensure it's a valid number
            
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
    print_schedules(schedules, movies_df, bumps)