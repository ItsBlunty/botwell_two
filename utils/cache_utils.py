from datetime import datetime, timedelta, timezone
from utils.search_utils import search_results

def cleanup_old_messages(message_cache):
    current_time = datetime.now(timezone.utc)
    week_ago = current_time - timedelta(days=7)
    
    expired = [msg_id for msg_id, msg_data in message_cache.items()
              if msg_data['timestamp'] < week_ago]
    
    for msg_id in expired:
        del message_cache[msg_id]
    
    return len(expired)

def cleanup_old_searches():
    current_time = datetime.now()
    expired = [user_id for user_id, data in search_results.items()
               if current_time - data['timestamp'] > timedelta(minutes=120)]
    for user_id in expired:
        del search_results[user_id]