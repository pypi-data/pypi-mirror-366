import os
import tempfile
import uuid
from datetime import datetime, timedelta
from qv_session_manager.session_manager import SessionManager
from qv_ollama_sdk.domain.models import Conversation, Message, MessageRole

def test_session_manager_workflow():
    # Temporary DB for test (close handle immediately to avoid PermissionError)
    fd, db_path = tempfile.mkstemp()
    os.close(fd)
    try:
        mgr = SessionManager(db_path=db_path)
        # 1. Create Conversation & Messages
        conv = Conversation(model_name="llama3", title="Test", metadata={"foo": "bar"})
        conv.add_user_message("Hello")
        conv.add_assistant_message("Hi! How can I help?")
        # 2. Save
        mgr.save_conversation(conv, conv.messages)
        # 3. Load
        loaded = mgr.load_conversation(str(conv.id))
        assert loaded.id == conv.id
        assert loaded.title == "Test"
        assert loaded.model_name == "llama3"  # Check that model_name is correctly saved/loaded
        assert len(loaded.messages) == 2
        # 4. List
        all_convs = mgr.list_conversations()
        assert any(c["id"] == str(conv.id) for c in all_convs)
        # 5. Search
        found = mgr.search_conversations("Hello")
        assert any(c["id"] == str(conv.id) for c in found)
        # 6. Time search
        now = datetime.now().isoformat()
        found_time = mgr.search_by_time(start=now[:10])
        assert any(c["id"] == str(conv.id) for c in found_time)
        # 7. Resume
        resumed = mgr.resume_conversation(str(conv.id))
        assert resumed["last_message"]["content"] == "Hi! How can I help?"
        # 8. Delete
        mgr.delete_conversation(str(conv.id))
        assert mgr.load_conversation(str(conv.id)) is None
    finally:
        try:
            os.remove(db_path)
        except PermissionError:
            # Windows-specific issue: SQLite file still in use
            pass

def test_backward_compatibility():
    """Test backward compatibility with old database schema (without model_name column)."""
    fd, db_path = tempfile.mkstemp()
    os.close(fd)
    try:
        # Create old schema manually (without model_name)
        with sqlite3.connect(db_path) as conn:
            conn.executescript("""
                CREATE TABLE conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    metadata TEXT
                );
                CREATE TABLE messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    created_at TEXT,
                    metadata TEXT,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );
            """)
        
        # Test that SessionManager can handle old schema
        mgr = SessionManager(db_path=db_path)
        
        # Create and save conversation (should trigger migration)
        conv = Conversation(model_name="gemma2:2b", title="Backward Test", metadata={"test": "backward"})
        conv.add_user_message("Hello from old schema!")
        conv.add_assistant_message("Hi! I'm from the old schema too!")
        
        mgr.save_conversation(conv, conv.messages)
        
        # Load conversation (should work with fallback model_name)
        loaded = mgr.load_conversation(str(conv.id))
        assert loaded.id == conv.id
        assert loaded.title == "Backward Test"
        assert loaded.model_name == "gemma2:2b"  # Should be saved correctly now
        assert len(loaded.messages) == 2
        
        print("✅ Backward compatibility test passed!")
        
    finally:
        try:
            os.remove(db_path)
        except PermissionError:
            pass

if __name__ == "__main__":
    test_session_manager_workflow()
    test_backward_compatibility()
    print("SessionManager tests successful!") 