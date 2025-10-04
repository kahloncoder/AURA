import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Sparkles, LogOut, Plus, Clock, History } from "lucide-react";
import { toast } from "sonner";
import { roomsApi } from "@/services/api";

interface Room {
  name: string;
  description: string;
  session_duration_minutes: number;
  greeting: string;
  agents: Array<{
    name: string;
    voice: string;
    system_prompt: string;
  }>;
}

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<any>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    const userData = localStorage.getItem("aura_user");
    if (!userData) {
      navigate("/auth");
      return;
    }
    setUser(JSON.parse(userData));

    // Fetch rooms from backend
    fetchRooms();
  }, [navigate]);

  const fetchRooms = async () => {
    try {
      setLoading(true);

      // Call the backend API to get the list of rooms
      const data = await roomsApi.getRooms();
      
      // Correctly access the "rooms" array inside the response
      setRooms(data.rooms); 

    } catch (error) {
      console.error("Error fetching rooms:", error);
      toast.error("Failed to load rooms. Is the backend server running?");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("aura_user");
    toast.success("Logged out successfully");
    navigate("/");
  };

  const startSession = (room: Room) => {
    navigate("/chat", { state: { room } });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-hero flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading rooms...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-hero">
      {/* Navigation */}
      <nav className="border-b border-border/50 backdrop-blur-lg bg-background/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold gradient-text">AURA</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground hidden sm:block">
                Welcome, {user?.name || user?.email}
              </span>
              <Button onClick={() => navigate("/blog")} variant="ghost" size="sm">
                Blog
              </Button>
              <Button onClick={() => navigate("/conversations")} variant="ghost" size="sm">
                <History className="w-4 h-4 mr-2" />
                History
              </Button>
              <Button onClick={handleLogout} variant="outline" size="sm">
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold mb-3">
            Choose Your <span className="gradient-text">Conversation Room</span>
          </h1>
          <p className="text-xl text-muted-foreground">
            Select a scenario to start your multi-agent voice session
          </p>
        </div>

        {/* Rooms Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {rooms.map((room, idx) => (
            <Card
              key={idx}
              className="p-6 bg-card border-border/50 hover:border-primary/50 transition-all hover:shadow-elegant cursor-pointer group"
              onClick={() => startSession(room)}
            >
              <div className="mb-4">
                <h3 className="text-2xl font-bold mb-2 group-hover:text-primary transition-colors">
                  {room.name}
                </h3>
                <p className="text-muted-foreground mb-4">{room.description}</p>
              </div>

              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  <span>{room.session_duration_minutes} minute session</span>
                </div>

                <div className="flex flex-wrap gap-2">
                  {room.agents.map((agent, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-muted rounded-full text-xs text-muted-foreground"
                    >
                      {agent.name}
                    </span>
                  ))}
                </div>
              </div>

              <Button className="w-full mt-6 bg-gradient-primary hover:opacity-90 transition-opacity">
                Start Session
              </Button>
            </Card>
          ))}

          {/* Create Custom Room Card */}
          <Card className="p-6 bg-card border-border/50 border-dashed hover:border-primary/50 transition-all cursor-pointer group flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4 group-hover:bg-primary/10 transition-colors">
              <Plus className="w-8 h-8 text-muted-foreground group-hover:text-primary transition-colors" />
            </div>
            <h3 className="text-xl font-bold mb-2">Create Custom Room</h3>
            <p className="text-muted-foreground text-sm mb-4">
              Design your own multi-agent scenario
            </p>
            <Button variant="outline" className="border-border/50">
              Coming Soon
            </Button>
          </Card>
        </div>

        {/* Info Section */}
        <Card className="p-6 bg-card/50 border-border/50">
          <h3 className="text-lg font-semibold mb-3">How to use AURA effectively:</h3>
          <ul className="space-y-2 text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="text-primary mt-1">•</span>
              <span>Press and hold the microphone button while speaking your question</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary mt-1">•</span>
              <span>Be specific and clear - the agents work best with focused questions</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary mt-1">•</span>
              <span>Each session maintains context, so you can ask follow-up questions</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary mt-1">•</span>
              <span>Three specialized agents will process your input sequentially for comprehensive insights</span>
            </li>
          </ul>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
