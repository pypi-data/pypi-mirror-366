import os
import sys
import glob
import yaml
from keypractice.core import run_session
from keypractice.analytics import get_exercise_stats

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    # First try to find exercises in the package data
    package_dir = os.path.dirname(os.path.abspath(__file__))
    exercises_dir = os.path.join(package_dir, 'exercises')
    print(f"DEBUG: Package dir: {package_dir}")
    print(f"DEBUG: Exercises dir: {exercises_dir}")
    print(f"DEBUG: Exists: {os.path.exists(exercises_dir)}")
    
    # If not found in package, try project root
    if not os.path.exists(exercises_dir):
        exercises_dir = os.path.join(get_project_root(), 'exercises')
        print(f"DEBUG: Trying project root: {exercises_dir}")
        print(f"DEBUG: Exists: {os.path.exists(exercises_dir)}")
    
    if not os.path.exists(exercises_dir):
        print(f'No exercises directory found at {exercises_dir}. Creating one...')
        os.makedirs(exercises_dir)
    
    yaml_files = glob.glob(os.path.join(exercises_dir, '*.yaml'))
    print(f"DEBUG: Found YAML files: {yaml_files}")
    if not yaml_files:
        print('No exercise YAML files found. Please add some to the exercises/ directory.')
        return
    exercises = []
    for path in yaml_files:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            data['__file__'] = path
            exercises.append(data)
    while True:
        print('\nAvailable exercises:')
        for idx, ex in enumerate(exercises):
            name = ex.get('name', os.path.basename(ex['__file__']))
            print(f'{idx+1}. {name}')
        print('A. View analytics for an exercise')
        print('Q. Quit')
        choice = input('Select an exercise by number, or choose an option: ').strip().lower()
        if choice == 'q':
            print('Goodbye!')
            return
        if choice == 'a':
            try:
                ex_idx = int(input('Enter exercise number to view analytics: ')) - 1
                if not (0 <= ex_idx < len(exercises)):
                    print('Invalid choice.')
                    continue
            except ValueError:
                print('Invalid input.')
                continue
            ex = exercises[idx]
            stats = get_exercise_stats(ex.get('name', os.path.basename(ex['__file__'])))
            if not stats:
                print('No analytics found for this exercise.')
            else:
                print(f"\nAnalytics for {ex.get('name', os.path.basename(ex['__file__']))}:")
                print(f"  Best time: {stats.get('best_time', 'N/A')} seconds")
                print(f"  Best speed: {stats.get('best_speed', 'N/A')} WPM")
                print(f"  Lowest errors: {stats.get('lowest_errors', 'N/A')}")
                print(f"  Streak: {stats.get('streak', 0)} days")
                print(f"  Last session: {stats.get('last_session_date', 'N/A')}")
                print(f"  Last 5 sessions:")
                for s in stats.get('improvements', []):
                    print(f"    - Date: {s['date']}, Time: {s['time_taken']}s, Errors: {s['errors']}, Speed: {s['speed']} WPM")
            continue
        try:
            idx = int(choice) - 1
            if not (0 <= idx < len(exercises)):
                print('Invalid choice.')
                continue
        except ValueError:
            print('Invalid input.')
            continue
        run_session(exercises[idx])

if __name__ == '__main__':
    main() 