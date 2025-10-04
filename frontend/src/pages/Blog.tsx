import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { Sparkles, ArrowLeft, Lightbulb, Target, Zap, TrendingUp } from "lucide-react";

const Blog = () => {
  const navigate = useNavigate();

  const posts = [
    {
      icon: Lightbulb,
      title: "Getting Started with AURA",
      excerpt: "Learn how to maximize your first multi-agent conversation and get the most comprehensive insights.",
      content: [
        "AURA works by combining three specialized AI agents that each bring unique perspectives to your questions. Here's how to make the most of it:",
        "1. Choose the Right Room: Select a scenario that matches your need. Business Strategy for decisions, Career Planning for professional growth, or Technical Discussion for complex problems.",
        "2. Ask Clear Questions: Be specific. Instead of 'How do I grow my business?', try 'What are 3 strategies to increase customer retention in a SaaS company?'",
        "3. Listen to All Three Agents: Each agent builds on the previous response. The first analyzes, the second challenges, and the third provides practical steps.",
        "4. Use Follow-ups: AURA maintains context. Ask clarifying questions to dive deeper into any perspective that resonates with you."
      ]
    },
    {
      icon: Target,
      title: "Best Use Cases for Multi-Agent Intelligence",
      excerpt: "Discover scenarios where AURA's multi-perspective approach shines brightest.",
      content: [
        "Multi-agent conversations excel in situations requiring comprehensive analysis:",
        "Business Decisions: Get analytical data review, creative alternatives, and practical implementation steps all in one conversation.",
        "Career Planning: Receive strategic career advice, bold moves to consider, and realistic action plans simultaneously.",
        "Creative Projects: Explore analytical frameworks, provocative ideas, and executable steps for your creative endeavors.",
        "Technical Challenges: Break down complex problems with systematic analysis, innovative solutions, and pragmatic approaches.",
        "The key is using AURA when you need more than just one answer - when you want to explore a topic from multiple angles before deciding."
      ]
    },
    {
      icon: Zap,
      title: "Maximizing Session Efficiency",
      excerpt: "Tips and tricks to get the most value from your 5 or 15-minute AURA sessions.",
      content: [
        "Time is valuable in AURA sessions. Here's how to use it wisely:",
        "Prepare Your Question: Think about what you really need to know before starting. Write it down if needed.",
        "Start Broad, Then Narrow: Begin with your main question, then use follow-ups to explore specific aspects that interest you most.",
        "Take Notes: AURA provides rich, multi-layered insights. Have a notepad ready to capture key points from each agent.",
        "Focus on Actionability: If an agent's response is too theoretical, ask for specific next steps or concrete examples.",
        "Use the Full Duration: Don't stop after the first answer. The conversation gets richer as context builds.",
        "Pro tip: For complex topics, start with a 15-minute session to fully explore different perspectives and implications."
      ]
    },
    {
      icon: TrendingUp,
      title: "Advanced Strategies for Power Users",
      excerpt: "Take your AURA conversations to the next level with these advanced techniques.",
      content: [
        "Once you're comfortable with basic usage, try these advanced strategies:",
        "Persona Play: Frame your questions from different stakeholder perspectives. 'As a CEO vs. as a customer, how would you view this product?'",
        "Challenge Mode: Ask one agent to critique another's response. 'The Strategic Analyst suggested X, what are the risks?'",
        "Scenario Testing: Use AURA to explore multiple futures. 'What happens if I choose option A versus option B?'",
        "Iterative Refinement: Take insights from one session and use them to frame deeper questions in your next session.",
        "Cross-Room Learning: Use Business Strategy insights to inform your Career Planning conversations and vice versa.",
        "Remember: The more specific and thought-provoking your questions, the more valuable the multi-agent responses become."
      ]
    }
  ];

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
              <Button onClick={() => navigate("/")} variant="ghost" size="sm">
                Home
              </Button>
              <Button onClick={() => navigate("/auth")} variant="outline" size="sm">
                Sign In
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => navigate("/")}
          className="mb-8 hover:bg-card"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Home
        </Button>

        {/* Header */}
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold mb-4">
            <span className="gradient-text">AURA Guides</span>
          </h1>
          <p className="text-xl text-muted-foreground">
            Master multi-agent voice intelligence with our comprehensive guides
          </p>
        </div>

        {/* Blog Posts */}
        <div className="space-y-8">
          {posts.map((post, idx) => (
            <Card key={idx} className="p-8 bg-card border-border/50 hover:border-primary/50 transition-all hover:shadow-elegant">
              <div className="flex items-start gap-6">
                <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-gradient-primary flex items-center justify-center">
                  <post.icon className="w-6 h-6 text-primary-foreground" />
                </div>
                <div className="flex-1">
                  <h2 className="text-3xl font-bold mb-3">{post.title}</h2>
                  <p className="text-lg text-muted-foreground mb-6">{post.excerpt}</p>
                  <div className="space-y-4 text-foreground">
                    {post.content.map((paragraph, i) => (
                      <p key={i} className={paragraph.match(/^\d\./) ? "ml-4" : ""}>
                        {paragraph}
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* CTA */}
        <Card className="mt-12 p-8 bg-gradient-primary text-center">
          <h2 className="text-3xl font-bold mb-4 text-primary-foreground">
            Ready to Experience Multi-Agent Intelligence?
          </h2>
          <p className="text-lg mb-6 text-primary-foreground/90">
            Put these strategies into practice and discover the power of three perspectives
          </p>
          <Button
            size="lg"
            onClick={() => navigate("/auth")}
            className="bg-background text-foreground hover:bg-background/90"
          >
            Start Your First Session
          </Button>
        </Card>
      </div>

      {/* Footer */}
      <footer className="border-t border-border/50 py-8 px-4 sm:px-6 lg:px-8 mt-20">
        <div className="max-w-7xl mx-auto text-center text-muted-foreground">
          <p>&copy; 2025 AURA. Multi-Agent Voice Intelligence Platform.</p>
        </div>
      </footer>
    </div>
  );
};

export default Blog;
