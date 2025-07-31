import os
import json
from datetime import datetime

def get_analytics_path():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return os.path.join(data_dir, 'analytics.json')

def load_analytics():
    path = get_analytics_path()
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_analytics(data):
    path = get_analytics_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# New functions for analytics tracking

def record_session(exercise_name, time_taken, errors, speed):
    """Record a session for an exercise, updating analytics."""
    analytics = load_analytics()
    now = datetime.now().isoformat()
    ex_stats = analytics.get(exercise_name, {
        'sessions': [],
        'best_time': None,
        'best_speed': None,
        'lowest_errors': None,
        'streak': 0,
        'last_session_date': None,
        'improvements': [],
    })
    # Update bests
    if ex_stats['best_time'] is None or time_taken < ex_stats['best_time']:
        ex_stats['best_time'] = time_taken
    if ex_stats['best_speed'] is None or speed > ex_stats['best_speed']:
        ex_stats['best_speed'] = speed
    if ex_stats['lowest_errors'] is None or errors < ex_stats['lowest_errors']:
        ex_stats['lowest_errors'] = errors
    # Streak logic (daily streak)
    last_date = ex_stats['last_session_date']
    today = datetime.now().date()
    if last_date:
        last = datetime.fromisoformat(last_date).date()
        if (today - last).days == 1:
            ex_stats['streak'] += 1
        elif (today - last).days > 1:
            ex_stats['streak'] = 1
    else:
        ex_stats['streak'] = 1
    ex_stats['last_session_date'] = now
    # Record session
    session = {
        'date': now,
        'time_taken': time_taken,
        'errors': errors,
        'speed': speed,
    }
    ex_stats['sessions'].append(session)
    # Track improvements (last 5 sessions)
    ex_stats['improvements'] = ex_stats['sessions'][-5:]
    analytics[exercise_name] = ex_stats
    save_analytics(analytics)


def get_exercise_stats(exercise_name):
    analytics = load_analytics()
    return analytics.get(exercise_name, None)


def get_all_stats():
    return load_analytics() 