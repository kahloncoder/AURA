"""
AURA Session Management
Handles conversation sessions, context, and agent processing with streaming
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from config import *


# ============================================================================
# SESSION MANAGER
# ============================================================================

class SessionManager:
    """
    Manages conversation sessions with pseudo-streaming agent responses
    Prepared for future MongoDB integration
    """
    
    def __init__(self, room, duration_minutes):
        self.room = room
        self.start_time = datetime.now()
        self.duration = timedelta(minutes=duration_minutes)
        self.end_time = self.start_time + self.duration
        self.conversation_log = []
        self.context = []
        
        # File-based logging
        self.log_dir = Path(LOGS_DIR)
        self.log_dir.mkdir(exist_ok=True)
        
        # MongoDB (for future use)
        # self.session_id = None
        # self._create_mongodb_session()
    
    # def _create_mongodb_session(self):
    #     """Create new session in MongoDB"""
    #     from database import db
    #     if db is not None:
    #         session_doc = {
    #             "room_name": self.room['name'],
    #             "start_time": self.start_time,
    #             "status": "active",
    #             "conversation": []
    #         }
    #         result = db.sessions.insert_one(session_doc)
    #         self.session_id = result.inserted_id
    
    def is_expired(self):
        """Check if session time expired"""
        return datetime.now() >= self.end_time
    
    def remaining_time(self):
        """Get remaining seconds"""
        remaining = self.end_time - datetime.now()
        return max(0, int(remaining.total_seconds()))
    
    def log_interaction(self, role, content, agent_name=None):
        """
        Log conversation interaction
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            agent_name: Optional agent name
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content
        }
        if agent_name:
            log_entry["agent"] = agent_name
        
        self.conversation_log.append(log_entry)
        
        # MongoDB update (for future)
        # if db and self.session_id:
        #     db.sessions.update_one(
        #         {"_id": self.session_id},
        #         {"$push": {"conversation": log_entry}}
        #     )
    
    def get_voice_for_agent(self, agent, agent_index):
        """
        Get voice for agent with fallback
        
        Args:
            agent: Agent config dict
            agent_index: Agent position (0, 1, 2)
            
        Returns:
            str: Valid Deepgram voice
        """
        voice = agent.get('voice', '').strip()
        
        # Validate voice
        if voice and voice.startswith('aura-'):
            return voice
        
        # Fallback to default
        return DEFAULT_VOICES[agent_index % len(DEFAULT_VOICES)]
    
    def process_agents_streaming(self, user_text, llm_handler, deepgram_handler, emit_callback):
        """
        Process user input through agents with PSEUDO-STREAMING
        
        Flow:
        1. Agent 1 thinks → generates audio → SEND TO FRONTEND (plays while Agent 2 thinks)
        2. Agent 2 thinks → generates audio → SEND TO FRONTEND (plays while Agent 3 thinks)
        3. Agent 3 thinks → generates audio → SEND TO FRONTEND
        
        Args:
            user_text: User's transcribed input
            llm_handler: CerebrasHandler instance
            deepgram_handler: DeepgramHandler instance
            emit_callback: SocketIO emit function
            
        Returns:
            list: Agent responses [(name, text), ...]
        """
        agent_responses = []
        agents = self.room['agents']
        
        print(f"\n🎯 Processing {len(agents)} agents (streaming mode)")
        
        for idx, agent in enumerate(agents):
            agent_name = agent.get('name', f'Agent {idx + 1}')
            
            # Notify: Agent is thinking
            emit_callback('agent_status', {
                'agent': agent_name,
                'status': 'thinking',
                'message': f'{agent_name} is thinking...'
            })
            
            # Build LLM messages
            messages = [{"role": "system", "content": agent['system_prompt']}]
            
            # Add recent context
            for ctx in self.context[-MAX_CONTEXT_MESSAGES:]:
                messages.append(ctx)
            
            # Add user input + previous agent responses
            if agent_responses:
                context_text = f"User: {user_text}\n\nPrevious responses:\n"
                for prev_name, prev_resp in agent_responses:
                    context_text += f"{prev_name}: {prev_resp}\n"
                messages.append({"role": "user", "content": context_text})
            else:
                messages.append({"role": "user", "content": user_text})
            
            # Get LLM response
            response = llm_handler.chat(messages)
            
            if not response:
                # Fallback response
                response = f"I'm {agent_name}. Let me think about that."
                print(f"⚠️ Using fallback for {agent_name}")
            
            agent_responses.append((agent_name, response))
            print(f"✅ {agent_name}: {response[:60]}...")
            
            # Log this response
            self.log_interaction('assistant', response, agent_name=agent_name)
            
            # Get voice
            voice = self.get_voice_for_agent(agent, idx)
            
            # Notify: Agent is speaking
            emit_callback('agent_status', {
                'agent': agent_name,
                'status': 'speaking',
                'message': f'{agent_name} is speaking...'
            })
            
            # Generate audio
            audio_b64 = deepgram_handler.synthesize(response, voice)
            
            # IMMEDIATELY send to frontend (streaming)
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
        
        # Update context
        final_combined = " ".join([resp[1] for resp in agent_responses])
        self.context.extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": final_combined}
        ])
        
        return agent_responses
    
    def save_log(self):
        """Save conversation to file"""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        filename = self.log_dir / f"aura_{self.room['name'].replace(' ', '_')}_{timestamp}.json"
        
        session_data = {
            "room": self.room['name'],
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "conversation": self.conversation_log
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Session saved: {filename}")
        
        # MongoDB version (for future)
        # if db and self.session_id:
        #     db.sessions.update_one(
        #         {"_id": self.session_id},
        #         {"$set": {
        #             "end_time": datetime.now(),
        #             "status": "completed",
        #             "duration_seconds": session_data["duration_seconds"]
        #         }}
        #     )