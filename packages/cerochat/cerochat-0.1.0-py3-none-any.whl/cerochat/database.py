from supabase import create_client
from cerochat.config import SUPABASE_URL, SUPABASE_API_KEY
from supabase.lib.client_options import ClientOptions
from datetime import datetime

# Увеличиваем таймаут для транзакций
client_options = ClientOptions(postgrest_client_timeout=10)
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY, options=client_options)

def insert_message(username: str, message: str):
    supabase.table("messages").insert({
        "username": username,
        "message": message
    }).execute()

def get_messages(after_id: int = 0):
    return supabase.table("messages") \
        .select("*") \
        .gt("id", after_id) \
        .order("id", desc=False) \
        .execute().data

def delete_messages_by_username(username: str):
    supabase.table("messages").delete().eq("username", username).execute()

def get_last_message_id():
    result = supabase.table("messages") \
        .select("id") \
        .order("id", desc=True) \
        .limit(1) \
        .execute()
    return result.data[0]["id"] if result.data else 0

def reserve_username(username: str) -> bool:
    try:
        result = supabase.rpc('reserve_username', {'p_username': username}).execute()
        return result.data
    except Exception as e:
        print(f"Error reserving username: {e}")
        return False