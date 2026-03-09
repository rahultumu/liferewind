import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime

# load dotenv from this file's directory (backend/.env)
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

BASE_MEM_URL = f"{SUPABASE_URL}/rest/v1/memories"
BASE_USER_URL = f"{SUPABASE_URL}/rest/v1/users"


def init_tables():
    # ensure tables exist via dashboard; nothing to do programmatically
    print("Supabase REST client ready (ensure tables exist in dashboard)")

    # if a direct database URL is provided, attempt to create tables automatically
    db_url = os.getenv("SUPABASE_DB_URL")
    if db_url:
        try:
            import psycopg2
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id bigserial PRIMARY KEY,
                    user_email text,
                    content text,
                    type text,
                    metadata jsonb,
                    created_at timestamp
                );
                CREATE TABLE IF NOT EXISTS users (
                    id bigserial PRIMARY KEY,
                    email text UNIQUE,
                    phone text,
                    password text,
                    created_at timestamp
                );
                """
            )
            conn.commit()
            cur.close()
            conn.close()
            print("Created tables via direct DB connection")
        except Exception as e:
            print(f"Could not create tables via DB URL: {e}")
    return True


def add_memory(user_email, text, memory_type="text", metadata=None):
    data = {
        "user_email": user_email,
        "content": text,
        "type": memory_type,
        "metadata": metadata or {},
        "created_at": datetime.utcnow().isoformat()
    }
    try:
        r = requests.post(BASE_MEM_URL, headers=HEADERS, data=json.dumps(data))
        if r.status_code in (200, 201):
            return {"status": "success", "id": r.json()[0].get("id")}
        else:
            return {"status": "error", "message": r.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_memories(user_email, limit=100):
    try:
        params = {"user_email": f"eq.{user_email}", "order": "created_at.desc", "limit": limit}
        r = requests.get(BASE_MEM_URL, headers=HEADERS, params=params)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        print(f"Error fetching memories: {e}")
        return []


def get_memory_by_date(user_email, date_str):
    try:
        params = {"user_email": f"eq.{user_email}", "created_at": f"like.{date_str}%"}
        r = requests.get(BASE_MEM_URL, headers=HEADERS, params=params)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        print(f"Error fetching memories by date: {e}")
        return []


def get_all_memory_texts(user_email):
    try:
        mems = get_memories(user_email, limit=1000)
        return "\n".join([m.get("content", "") for m in mems])
    except Exception as e:
        print(f"Error getting memory texts: {e}")
        return ""


def get_memory_stats(user_email):
    try:
        mems = get_memories(user_email, limit=1000)
        total = len(mems)
        dates = set(m.get("created_at", "")[:10] for m in mems if m.get("created_at"))
        return {"total_memories": total, "days_with_memories": len(dates)}
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {"total_memories":0, "days_with_memories":0}


def delete_memory(memory_id):
    try:
        r = requests.delete(BASE_MEM_URL, headers=HEADERS, params={"id": f"eq.{memory_id}"})
        return {"status": "success"} if r.status_code in (200,204) else {"status":"error","message":r.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def update_memory(memory_id, content):
    try:
        r = requests.patch(BASE_MEM_URL, headers=HEADERS, params={"id": f"eq.{memory_id}"}, data=json.dumps({"content": content}))
        return {"status": "success"} if r.status_code in (200,204) else {"status":"error","message":r.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def user_exists(email):
    try:
        r = requests.get(BASE_USER_URL, headers=HEADERS, params={"email": f"eq.{email}"})
        return len(r.json()) > 0
    except Exception as e:
        print(f"Error checking user: {e}")
        return False


def add_user(email, phone, password):
    data = {"email": email, "phone": phone, "password": password, "created_at": datetime.utcnow().isoformat()}
    try:
        r = requests.post(BASE_USER_URL, headers=HEADERS, data=json.dumps(data))
        return {"status": "success"} if r.status_code in (200,201) else {"status":"error","message":r.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_user(email):
    try:
        r = requests.get(BASE_USER_URL, headers=HEADERS, params={"email": f"eq.{email}"})
        arr = r.json()
        return arr[0] if arr else None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def import_from_json(json_path, user_email=None):
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        return {"status": "error", "message": f"Failed reading JSON: {e}"}
    count = 0
    errors = []
    for entry in data:
        text = entry if isinstance(entry, str) else entry.get("content", "")
        if not text:
            continue
        res = add_memory(user_email or "unknown", text)
        if res.get("status") == "success":
            count += 1
        else:
            errors.append(res.get("message"))
    result = {"status": "success", "imported": count}
    if errors:
        result["errors"] = errors
    return result


# initialize
if SUPABASE_URL and SUPABASE_KEY:
    init_tables()
else:
    print("Warning: Supabase credentials missing, cannot connect")
