import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { 
  Search, 
  MessageSquare, 
  Scale, 
  BookOpen, 
  Gavel, 
  Shield,
  Sparkles,
  ArrowRight,
  CheckCircle2
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const Landing = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: BookOpen,
      title: 'Bharatiya Nyaya Sanhita',
      description: '356 sections covering criminal offences and punishments',
      badge: 'BNS',
      color: 'text-blue-600 dark:text-blue-400'
    },
    {
      icon: Gavel,
      title: 'Bharatiya Nagarik Suraksha Sanhita',
      description: '533 sections on criminal procedures and investigations',
      badge: 'BNSS',
      color: 'text-purple-600 dark:text-purple-400'
    },
    {
      icon: Scale,
      title: 'Bharatiya Sakshya Adhiniyam',
      description: '170 sections on evidence laws and admissibility',
      badge: 'BSA',
      color: 'text-amber-600 dark:text-amber-400'
    }
  ];

  const capabilities = [
    'AI-powered semantic search across all acts',
    'Instant legal provision retrieval',
    'Interactive chatbot for legal queries',
    'Cross-reference related sections',
    'Simple and advanced search modes',
    'Real-time legal assistance'
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-secondary/5 to-justice-gold/5 dark:from-primary/10 dark:via-secondary/10 dark:to-justice-gold/10" />
        <div className="container mx-auto max-w-6xl relative z-10">
          <div className="text-center mb-12 animate-in fade-in slide-in-from-bottom duration-700">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary mb-6">
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-medium">Powered by Advanced AI</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary via-secondary to-justice-gold bg-clip-text text-transparent">
              Section Sense
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
              Your intelligent companion for navigating India's new criminal justice system
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button 
                size="lg" 
                onClick={() => navigate('/search')}
                className="bg-primary hover:bg-primary-hover text-white shadow-legal hover:shadow-glow transition-all duration-300 group"
              >
                <Search className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
                Start Searching
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button 
                size="lg" 
                variant="outline"
                onClick={() => navigate('/chat')}
                className="border-2 hover:bg-secondary/10 hover:border-secondary transition-all duration-300 group"
              >
                <MessageSquare className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
                Chat with Kamado
              </Button>
            </div>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-6 mb-16 animate-in fade-in slide-in-from-bottom duration-700 delay-200">
            {features.map((feature, index) => (
              <Card key={index} className="card-enhanced hover:scale-105 transition-transform duration-300">
                <CardHeader>
                  <div className="flex items-center justify-between mb-2">
                    <feature.icon className={`w-8 h-8 ${feature.color}`} />
                    <span className="text-xs font-bold px-2 py-1 rounded bg-primary/10 text-primary">
                      {feature.badge}
                    </span>
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="animate-in fade-in slide-in-from-left duration-700">
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Powerful Legal Search at Your Fingertips
              </h2>
              <p className="text-muted-foreground mb-6 text-lg">
                Leverage cutting-edge AI technology to instantly find relevant legal provisions 
                across BNS, BNSS, and BSA. Get accurate results in seconds, not hours.
              </p>
              <div className="space-y-3">
                {capabilities.map((capability, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-success mt-0.5 flex-shrink-0" />
                    <span className="text-muted-foreground">{capability}</span>
                  </div>
                ))}
              </div>
              <Button 
                size="lg" 
                onClick={() => navigate('/search')}
                className="mt-8 bg-primary hover:bg-primary-hover text-white"
              >
                Try Legal Search
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>

            <div className="relative animate-in fade-in slide-in-from-right duration-700">
              <div className="relative rounded-2xl overflow-hidden shadow-elevated border bg-card p-8">
                <div className="flex items-center gap-2 mb-6">
                  <Search className="w-6 h-6 text-primary" />
                  <h3 className="font-semibold text-xl">Advanced Legal Search</h3>
                </div>
                <div className="space-y-4">
                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground mb-2">Example Query:</p>
                    <p className="font-medium">"Provisions related to theft and robbery"</p>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Shield className="w-4 h-4" />
                    <span>Instant results from 1,056+ legal sections</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Chat Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="relative animate-in fade-in slide-in-from-left duration-700 order-2 md:order-1">
              <div className="relative rounded-2xl overflow-hidden shadow-elevated border bg-card p-8">
                <div className="flex items-center gap-2 mb-6">
                  <MessageSquare className="w-6 h-6 text-secondary" />
                  <h3 className="font-semibold text-xl">AI Legal Assistant</h3>
                </div>
                <div className="space-y-4">
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                      <MessageSquare className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-muted rounded-2xl rounded-tl-sm p-4 flex-1">
                      <p className="text-sm">What is the punishment for theft under BNS?</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                      <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-primary/10 rounded-2xl rounded-tl-sm p-4 flex-1">
                      <p className="text-sm">Under BNS Section 303, theft is punishable with imprisonment...</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="animate-in fade-in slide-in-from-right duration-700 order-1 md:order-2">
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Chat with Your Legal Expert
              </h2>
              <p className="text-muted-foreground mb-6 text-lg">
                Get instant answers to your legal questions. Kamado understands context, 
                provides detailed explanations, and references relevant sections automatically.
              </p>
              <div className="space-y-3 mb-8">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-success mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">Natural language understanding</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-success mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">Contextual legal advice</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-success mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">24/7 availability</span>
                </div>
              </div>
              <Button 
                size="lg" 
                onClick={() => navigate('/chat')}
                className="bg-secondary hover:bg-secondary-hover text-white"
              >
                Start Chatting
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-primary via-secondary to-justice-gold">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Transform Your Legal Research?
          </h2>
          <p className="text-white/90 text-lg mb-8 max-w-2xl mx-auto">
            Join legal professionals using Kamado to navigate India's criminal justice system with confidence.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              onClick={() => navigate('/search')}
              className="bg-white text-primary hover:bg-white/90 shadow-lg"
            >
              Get Started Now
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Landing;
