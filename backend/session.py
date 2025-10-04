"""
AURA Session Management
Handles conversation sessions, context, and agent processing with MongoDB
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from config import *
from database import db # <-- ADDED: Import the database object


# ============================================================================
# SESSION MANAGER
# ============================================================================

class SessionManager:
    """
    Manages conversation sessions with pseudo-streaming agent responses
    and MongoDB persistence.
    """
    
    def __init__(self, room, duration_minutes):
        self.room = room
        self.start_time = datetime.now()
        self.duration = timedelta(minutes=duration_minutes)
        self.end_time = self.start_time + self.duration
        self.conversation_log = [] # Kept for in-memory context
        self.context = []
        
        # --- MODIFIED: MongoDB is now the primary session store ---
        self.session_id = None
        self._create_mongodb_session()
    
    def _create_mongodb_session(self):
        """Create a new session document in MongoDB"""
        if db is not None:
            try:
                session_doc = {
                    "room_name": self.room['name'],
                    "start_time": self.start_time,
                    "status": "active",
                    "conversation": []
                }
                result = db.sessions.insert_one(session_doc)
                self.session_id = result.inserted_id
                print(f"📄 New MongoDB session created with ID: {self.session_id}")
            except Exception as e:
                print(f"❌ MongoDB session creation error: {e}")
    
    def is_expired(self):
        """Check if session time expired"""
        return datetime.now() >= self.end_time
    
    def remaining_time(self):
        """Get remaining seconds"""
        remaining = self.end_time - datetime.now()
        return max(0, int(remaining.total_seconds()))
    
    def log_interaction(self, role, content, agent_name=None):
        """
        Log conversation interaction to memory and MongoDB in real-time.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content
        }
        if agent_name:
            log_entry["agent"] = agent_name
        
        self.conversation_log.append(log_entry)
        
        # --- MODIFIED: Push each message to the DB as it happens ---
        if db is not None and self.session_id:
            try:
                db.sessions.update_one(
                    {"_id": self.session_id},
                    {"$push": {"conversation": log_entry}}
                )
            except Exception as e:
                print(f"❌ MongoDB log update error: {e}")
    
    def get_voice_for_agent(self, agent, agent_index):
        """Get voice for agent with fallback"""
        voice = agent.get('voice', '').strip()
        if voice and voice.startswith('aura-'):
            return voice
        return DEFAULT_VOICES[agent_index % len(DEFAULT_VOICES)]
    
    def process_agents_streaming(self, user_text, llm_handler, deepgram_handler, emit_callback):
        """
        Process user input through agents with PSEUDO-STREAMING.
        """
        agent_responses = []
        agents = self.room['agents']
        
        print(f"\n🎯 Processing {len(agents)} agents (streaming mode)")
        
        for idx, agent in enumerate(agents):
            agent_name = agent.get('name', f'Agent {idx + 1}')
            
            emit_callback('agent_status', {
                'agent': agent_name, 'status': 'thinking',
                'message': f'{agent_name} is thinking...'
            })
            
            messages = [{"role": "system", "content": agent['system_prompt']}]
            for ctx in self.context[-MAX_CONTEXT_MESSAGES:]:
                messages.append(ctx)
            
            if agent_responses:
                context_text = f"User: {user_text}\n\nPrevious responses:\n"
                for prev_name, prev_resp in agent_responses:
                    context_text += f"{prev_name}: {prev_resp}\n"
                messages.append({"role": "user", "content": context_text})
            else:
                messages.append({"role": "user", "content": user_text})
            
            response = llm_handler.chat(messages)
            if not response:
                response = f"I'm {agent_name}. Let me think about that."
                print(f"⚠️ Using fallback for {agent_name}")
            
            agent_responses.append((agent_name, response))
            print(f"✅ {agent_name}: {response[:60]}...")
            self.log_interaction('assistant', response, agent_name=agent_name)
            
            voice = self.get_voice_for_agent(agent, idx)
            audio_b64 = deepgram_handler.synthesize(response, voice)
            
            if audio_b64:
                emit_callback('agent_response', {
                    'agent': agent_name,
                    'text': response,
                    'audio': audio_b64,
                    'voice': voice,
                    'remaining_time': self.remaining_time(),
                    'agent_index': idx,
                    'total_agents': len(agents)
                })
                print(f"📤 Streamed {agent_name}'s response to frontend")
            else:
                print(f"⚠️ Audio generation failed for {agent_name}")
        
        final_combined = " ".join([resp[1] for resp in agent_responses])
        self.context.extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": final_combined}
        ])
        
        return agent_responses
    
    def save_log(self):
        """Finalize the session log in MongoDB."""
        
        # --- MODIFIED: This function now updates the DB record instead of writing a file ---
        if db is not None and self.session_id:
            try:
                end_time = datetime.now()
                duration = (end_time - self.start_time).total_seconds()
                
                db.sessions.update_one(
                    {"_id": self.session_id},
                    {"$set": {
                        "end_time": end_time,
                        "status": "completed",
                        "duration_seconds": duration
                    }}
                )
                print(f"💾 Session {self.session_id} finalized in MongoDB.")
            except Exception as e:
                print(f"❌ MongoDB finalization error: {e}")
        else:
            print("⚠️ MongoDB not connected. Could not finalize session in DB.")