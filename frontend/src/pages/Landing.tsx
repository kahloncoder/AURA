import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { Mic, Users, Zap, Brain, Sparkles, ArrowRight } from "lucide-react";

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-hero">
      {/* Navigation */}
      <nav className="border-b border-border/50 backdrop-blur-lg bg-background/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold gradient-text">AURA</span>
            </div>
            <div className="hidden md:flex items-center gap-6">
              <button onClick={() => navigate("/blog")} className="text-muted-foreground hover:text-foreground transition-colors">
                Blog
              </button>
              <button onClick={() => navigate("/auth")} className="text-muted-foreground hover:text-foreground transition-colors">
                Sign In
              </button>
              <Button onClick={() => navigate("/auth")} className="bg-gradient-primary hover:opacity-90 transition-opacity">
                Get Started
              </Button>
            </div>
            <div className="md:hidden">
              <Button onClick={() => navigate("/auth")} size="sm" className="bg-gradient-primary">
                Sign In
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-glow opacity-30 blur-3xl" />
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-card border border-border/50 mb-8 fade-in-up">
            <Zap className="w-4 h-4 text-primary" />
            <span className="text-sm text-muted-foreground">Multi-Agent Voice Intelligence</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 fade-in-up" style={{ animationDelay: "0.1s" }}>
            Voice Conversations
            <br />
            <span className="gradient-text">With Multiple AI Minds</span>
          </h1>
          
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-10 fade-in-up" style={{ animationDelay: "0.2s" }}>
            Experience the future of AI assistance. AURA combines multiple specialized AI agents 
            to give you comprehensive, multi-perspective responses through natural voice conversations.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center fade-in-up" style={{ animationDelay: "0.3s" }}>
            <Button 
              size="lg" 
              onClick={() => navigate("/auth")}
              className="bg-gradient-primary hover:opacity-90 transition-opacity text-lg px-8 py-6 shadow-glow"
            >
              Start Free Session
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              onClick={() => navigate("/blog")}
              className="border-border/50 hover:bg-card text-lg px-8 py-6"
            >
              Learn More
            </Button>
          </div>

          {/* Voice Visualization */}
          <div className="mt-16 flex items-center justify-center gap-2">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="w-2 h-12 bg-gradient-primary rounded-full voice-wave"
                style={{ animationDelay: `${i * 0.1}s` }}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-background/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              Why Choose <span className="gradient-text">AURA</span>?
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Three specialized AI agents work together to provide comprehensive insights
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="p-8 bg-card border-border/50 hover:border-primary/50 transition-all hover:shadow-elegant group">
              <div className="w-12 h-12 rounded-lg bg-gradient-primary flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Users className="w-6 h-6 text-primary-foreground" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Multiple Perspectives</h3>
              <p className="text-muted-foreground">
                Each conversation flows through three specialized agents with unique personalities, 
                giving you analytical, creative, and practical viewpoints.
              </p>
            </Card>

            <Card className="p-8 bg-card border-border/50 hover:border-primary/50 transition-all hover:shadow-elegant group">
              <div className="w-12 h-12 rounded-lg bg-gradient-primary flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Mic className="w-6 h-6 text-primary-foreground" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Natural Voice Interface</h3>
              <p className="text-muted-foreground">
                Speak naturally and hear responses instantly. Powered by advanced 
                speech-to-text and text-to-speech technology for seamless conversations.
              </p>
            </Card>

            <Card className="p-8 bg-card border-border/50 hover:border-primary/50 transition-all hover:shadow-elegant group">
              <div className="w-12 h-12 rounded-lg bg-gradient-primary flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Brain className="w-6 h-6 text-primary-foreground" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Scenario-Based Rooms</h3>
              <p className="text-muted-foreground">
                Choose from business strategy, career planning, technical discussions, 
                and more. Each room optimized for specific use cases.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">How AURA Works</h2>
            <p className="text-xl text-muted-foreground">Simple, powerful, and incredibly fast</p>
          </div>

          <div className="space-y-12">
            {[
              { step: "1", title: "Select a Room", description: "Choose from business strategy, career planning, technical discussions, or create your own custom scenario." },
              { step: "2", title: "Start Speaking", description: "Press and hold to speak your question. AURA listens and transcribes your voice in real-time." },
              { step: "3", title: "Get Multi-Agent Insights", description: "Three specialized AI agents process your input sequentially, each building on the previous response." },
              { step: "4", title: "Hear Comprehensive Response", description: "Receive a complete answer combining analytical, creative, and practical perspectives through natural voice." }
            ].map((item, idx) => (
              <div key={idx} className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-primary flex items-center justify-center text-xl font-bold">
                  {item.step}
                </div>
                <div>
                  <h3 className="text-2xl font-bold mb-2">{item.title}</h3>
                  <p className="text-muted-foreground text-lg">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 relative">
        <div className="absolute inset-0 bg-gradient-glow opacity-20 blur-3xl" />
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Experience
            <br />
            <span className="gradient-text">Multi-Agent Intelligence?</span>
          </h2>
          <p className="text-xl text-muted-foreground mb-10">
            Start your first conversation today. No credit card required.
          </p>
          <Button 
            size="lg"
            onClick={() => navigate("/auth")}
            className="bg-gradient-primary hover:opacity-90 transition-opacity text-lg px-12 py-6 shadow-glow"
          >
            Get Started Free
            <ArrowRight className="ml-2 w-5 h-5" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center text-muted-foreground">
          <p>&copy; 2025 AURA. Multi-Agent Voice Intelligence Platform.</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
