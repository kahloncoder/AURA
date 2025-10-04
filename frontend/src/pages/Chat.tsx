import { useEffect, useState, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Sparkles, Mic, MicOff, ArrowLeft, Clock, Volume2 } from "lucide-react";
import { toast } from "sonner";
import { socketService } from "@/services/socketService";
import { Socket } from "socket.io-client";

interface Message {
  role: "user" | "assistant";
  content: string;
  agent?: string;
  timestamp: string;
}

const Chat = () => {
  const audioQueueRef = useRef<string[]>([]);
  const isPlayingRef = useRef(false);

  const location = useLocation();
  const navigate = useNavigate();
  const room = location.state?.room;

  const [isRecording, setIsRecording] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [sessionActive, setSessionActive] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<Socket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [mimeType] = useState(MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/ogg');
  const recordingStartTime = useRef<number>(0);

  useEffect(() => {
    if (!room) {
      navigate("/dashboard");
      return;
    }

    // Connect to backend
    const socket = socketService.connect();
    socketRef.current = socket;

    // Initialize session
    initializeSession(socket);

    return () => {
      socket.emit('end_session');
      socketService.disconnect();
    };
  }, [room, navigate]);

  useEffect(() => {
    // Auto-scroll to latest message
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ==================================================================
  // MODIFICATION 1: The new queue processing function replaces the old `playAudioFromBase64`.
  // ==================================================================
  const processAudioQueue = () => {
    if (isPlayingRef.current || audioQueueRef.current.length === 0) {
      return;
    }

    isPlayingRef.current = true;
    const base64Audio = audioQueueRef.current.shift();

    if (!base64Audio) {
      isPlayingRef.current = false;
      return;
    }

    try {
      const audio = new Audio(`data:audio/wav;base64,${base64Audio}`);
      
      audio.onended = () => {
        isPlayingRef.current = false;
        processAudioQueue(); // Play the next item in the queue
      };

      audio.play().catch(err => {
        console.error('Audio play error:', err);
        isPlayingRef.current = false;
        processAudioQueue(); // Try the next item even if this one fails
      });

    } catch (error) {
      console.error('Error processing audio queue:', error);
      isPlayingRef.current = false;
    }
  };

  const initializeSession = (socket: Socket) => {
    // Setup socket listeners
    socket.on('session_started', (data) => {
      console.log('✅ Session started:', data);
      setSessionActive(true);
      setTimeRemaining(data.duration * 60);
      
      setMessages([{
        role: "assistant",
        content: data.greeting,
        timestamp: new Date().toISOString()
      }]);

      toast.success(`Session started: ${data.room}`);
    });

    socket.on('transcription', (data) => {
      console.log('📝 Transcription:', data.text);
      setMessages(prev => [...prev, {
        role: "user",
        content: data.text,
        timestamp: new Date().toISOString()
      }]);
    });

    socket.on('agent_status', (data) => {
      console.log(`🤖 ${data.agent}: ${data.status}`);
    });

    // ==================================================================
    // MODIFICATION 2: The 'agent_response' handler now uses the queue.
    // ==================================================================
    socket.on('agent_response', (data) => {
      console.log(`💬 Agent response from ${data.agent}`);
      
      setMessages(prev => [...prev, {
        role: "assistant",
        content: data.text,
        agent: data.agent,
        timestamp: new Date().toISOString()
      }]);

      // Add the incoming audio to our queue and start processing it
      if (data.audio) {
        audioQueueRef.current.push(data.audio);
        processAudioQueue();
      }

      setTimeRemaining(data.remaining_time);
    });

    socket.on('processing_complete', () => {
      console.log('✅ All agents finished');
      setIsProcessing(false);
    });

    socket.on('session_ended', () => {
      console.log('👋 Session ended');
      endSession();
    });

    socket.on('error', (data) => {
      console.error('❌ Error:', data);
      toast.error(data.message);
      if (!data.recoverable) {
        endSession();
      }
    });

    // Start session
    socket.emit('start_session', { room });

    // Start countdown
    const interval = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          endSession();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  };

  // The old `playAudioFromBase64` function is no longer needed.

  const checkMicrophonePermission = async () => {
    try {
      const permissions = await navigator.permissions.query({ name: 'microphone' as PermissionName });
      if (permissions.state === 'denied') {
        toast.error('Microphone access blocked. Please enable it in your browser settings and reload the page.');
        return false;
      }
      return true;
    } catch (error) {
      console.error('Permission check error:', error);
      return true;
    }
  };

  const startRecording = async () => {
    // This function remains unchanged
    try {
      console.log('Starting recording...');
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      audioChunksRef.current = [];
      
      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = e => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.start(250);
      setIsRecording(true);
      toast.success("Recording - speak now!");
    } catch (error) {
      console.error('Mic error:', error);
      if (error instanceof DOMException) {
        switch (error.name) {
          case 'NotAllowedError':
            toast.error('Microphone access denied. Please allow microphone access and try again.');
            break;
          case 'NotFoundError':
            toast.error('No microphone found. Please connect a microphone and try again.');
            break;
          default:
            toast.error(`Microphone error: ${error.message}`);
        }
      } else {
        toast.error('Could not access microphone. Please check your settings and try again.');
      }
      setIsProcessing(false);
    }
  };

  const stopRecording = async () => {
    // This function remains unchanged
    const MIN_RECORDING_TIME = 1000;
    const elapsedTime = Date.now() - (recordingStartTime.current || 0);
    
    if (elapsedTime < MIN_RECORDING_TIME) {
      await new Promise(resolve => setTimeout(resolve, MIN_RECORDING_TIME - elapsedTime));
    }
    if (!mediaRecorderRef.current || !socketRef.current) return;

    const mediaRecorder = mediaRecorderRef.current;
    
    mediaRecorder.onstop = async () => {
      setIsRecording(false);
      setIsProcessing(true);

      if (audioChunksRef.current.length === 0) {
        setIsProcessing(false);
        toast.error("No audio recorded");
        return;
      }
      
      const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64Audio = reader.result!.toString().split(',')[1];
        socketRef.current?.emit('process_audio', { audio: base64Audio });
      };
      reader.readAsDataURL(audioBlob);
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
    };

    mediaRecorder.stop();
  };

  const endSession = () => {
    setSessionActive(false);
    toast.success("Session ended. Conversation saved!");
    setTimeout(() => navigate("/dashboard"), 2000);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!room) return null;

  return (
    // The JSX part remains unchanged
    <div className="min-h-screen bg-gradient-hero flex flex-col">
      {/* Header */}
      <nav className="border-b border-border/50 backdrop-blur-lg bg-background/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate("/dashboard")}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Exit Session
              </Button>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded bg-gradient-primary flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-primary-foreground" />
                </div>
                <span className="font-semibold">{room.name}</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Clock className="w-4 h-4" />
                <span className="font-mono">{formatTime(timeRemaining)}</span>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={endSession}
              >
                End Session
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <Card
                className={`max-w-[80%] p-4 ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card border-border/50"
                }`}
              >
                {message.agent && (
                  <div className="flex items-center gap-2 mb-2 text-sm text-muted-foreground">
                    <Volume2 className="w-4 h-4" />
                    <span className="font-semibold">{message.agent}</span>
                  </div>
                )}
                <p className="whitespace-pre-wrap">{message.content}</p>
                <p className="text-xs opacity-70 mt-2">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </Card>
            </div>
          ))}
          
          {isProcessing && (
            <div className="flex justify-start">
              <Card className="p-4 bg-card border-border/50">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    {[...Array(3)].map((_, i) => (
                      <div
                        key={i}
                        className="w-2 h-2 bg-primary rounded-full animate-pulse"
                        style={{ animationDelay: `${i * 0.2}s` }}
                      />
                    ))}
                  </div>
                  <span className="text-sm text-muted-foreground">Agents are thinking...</span>
                </div>
              </Card>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Recording Controls */}
      <div className="border-t border-border/50 backdrop-blur-lg bg-background/50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex flex-col items-center gap-4">
            <button
              onMouseDown={startRecording}
              onMouseUp={stopRecording}
              onTouchStart={startRecording}
              onTouchEnd={stopRecording}
              disabled={!sessionActive || isProcessing}
              className={`w-20 h-20 rounded-full flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                isRecording
                  ? "bg-destructive animate-pulse shadow-glow"
                  : "bg-gradient-primary hover:opacity-90"
              }`}
            >
              {isRecording ? (
                <MicOff className="w-8 h-8 text-primary-foreground" />
              ) : (
                <Mic className="w-8 h-8 text-primary-foreground" />
              )}
            </button>
            <p className="text-sm text-muted-foreground text-center font-medium">
              {isRecording ? (
                <span className="text-destructive animate-pulse">
                  Recording... Release Button to Send
                </span>
              ) : isProcessing ? (
                "Processing, please wait..."
              ) : (
                <span>
                  Press and <strong className="text-primary font-bold">HOLD</strong> the button to speak
                </span>
              )}
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {room.agents.map((agent: any, idx: number) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-muted rounded-full text-xs text-muted-foreground"
                >
                  {agent.name}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;