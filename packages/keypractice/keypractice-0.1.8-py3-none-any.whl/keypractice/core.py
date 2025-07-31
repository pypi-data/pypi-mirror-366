import time
import random
from keypractice.analytics import record_session

def run_session(exercise):
    print(f"Starting session for: {exercise.get('name', 'Unnamed Exercise')}")
    items = exercise.get('items', [])
    if not items:
        print('No items to practice in this exercise.')
        return
    random.shuffle(items)
    input('Press Enter to start...')
    start_time = time.time()
    errors = 0
    total_chars = 0
    for idx, item in enumerate(items):
        print(f"\nItem {idx+1}/{len(items)}: {item}")
        user_input = input('Type: ')
        total_chars += len(item)
        if user_input != item:
            print('Incorrect!')
            errors += 1
        else:
            print('Correct!')
    end_time = time.time()
    time_taken = round(end_time - start_time, 2)
    speed = round((total_chars / 5) / (time_taken / 60), 2)  # WPM
    print(f"\nSession complete!")
    print(f"Time taken: {time_taken} seconds")
    print(f"Errors: {errors}")
    print(f"Speed: {speed} WPM")
    record_session(exercise.get('name', 'Unnamed Exercise'), time_taken, errors, speed)
    print("Session data saved to analytics.") 