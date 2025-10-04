import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { ArrowLeft, MessageSquare, Clock, Eye, Loader2 } from "lucide-react";
import { useConversations, ConversationSummary, ConversationLog } from "@/hooks/useConversations";
import { conversationsApi } from "@/services/api"; // Import the API service

const Conversations = () => {
  const navigate = useNavigate();
  const { conversations, loading } = useConversations();
  const [selectedLog, setSelectedLog] = useState<ConversationLog | null>(null);
  const [isLogLoading, setIsLogLoading] = useState(false);

  const handleViewDetails = async (summary: ConversationSummary) => {
    setIsLogLoading(true);
    setSelectedLog(null); // Clear previous log while loading
    try {
      // Fetch the full log on demand when the user clicks "View"
      const fullLog = await conversationsApi.getConversationById(summary.id);
      setSelectedLog(fullLog);
    } catch (error) {
      console.error("Failed to fetch conversation details:", error);
    } finally {
      setIsLogLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-hero">
      <nav className="border-b border-border/50 backdrop-blur-lg bg-background/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Button variant="ghost" size="sm" onClick={() => navigate("/dashboard")}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
            <h1 className="text-xl font-semibold">Conversation History</h1>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
        ) : conversations.length === 0 ? (
          <Card className="p-12 text-center">
            <MessageSquare className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            <h2 className="text-xl font-semibold mb-2">No Saved Conversations</h2>
            <p className="text-muted-foreground">Completed sessions from your backend will appear here.</p>
          </Card>
        ) : (
          <div className="grid gap-4">
            {conversations.map((conv) => (
              <Card key={conv.id} className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 pr-4">
                    <h3 className="text-lg font-semibold">{conv.roomName}</h3>
                    <p className="text-muted-foreground mb-4 line-clamp-2">{conv.preview}</p>
                    <div className="flex items-center flex-wrap gap-4 text-sm text-muted-foreground">
                      <Badge variant="secondary">{conv.date}</Badge>
                      <div className="flex items-center gap-1"><MessageSquare className="w-4 h-4" /><span>{conv.messageCount} messages</span></div>
                      <div className="flex items-center gap-1"><Clock className="w-4 h-4" /><span>{conv.duration}</span></div>
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <Button variant="outline" size="sm" onClick={() => handleViewDetails(conv)}>
                      <Eye className="w-4 h-4 mr-2" /> View Details
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      <Dialog open={isLogLoading || !!selectedLog} onOpenChange={() => setSelectedLog(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>{selectedLog?.room_name || "Loading..."}</DialogTitle>
            <DialogDescription>
              {selectedLog ? `Conversation from ${new Date(selectedLog.start_time).toLocaleString()}` : 'Fetching conversation log...'}
            </DialogDescription>
          </DialogHeader>
          <ScrollArea className="h-[60vh] pr-4">
            {isLogLoading ? (
              <div className="flex justify-center items-center h-full py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              </div>
            ) : (
              <div className="space-y-4">
                {selectedLog?.conversation.map((msg, idx) => (
                  <div key={idx}>
                    <div className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                        {msg.agent && <div className="text-xs font-semibold mb-1 opacity-70">{msg.agent}</div>}
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Conversations;