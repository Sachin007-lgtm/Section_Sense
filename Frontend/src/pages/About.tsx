import { Scale, BookOpen, Users, Gavel } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const About = () => {
  const features = [
    {
      icon: BookOpen,
      title: 'Legal Professionals',
      description: 'Quickly find relevant legal sections to strengthen your case arguments and legal research.',
    },
    {
      icon: Users,
      title: 'Law Students',
      description: 'Study effectively by connecting case scenarios to specific legal provisions and understanding their applications.',
    },
    {
      icon: Gavel,
      title: 'Judges & Legal Experts',
      description: 'Streamline legal proceedings by rapidly identifying applicable laws and precedents.',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <Scale className="h-16 w-16 text-primary" />
          </div>
          <h1 className="font-merriweather font-bold text-4xl md:text-5xl text-foreground mb-6">
            About Section Sense
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Empowering legal professionals with AI-powered semantic matching to bridge the gap between case descriptions and relevant legal sections.
          </p>
        </div>

        <div className="space-y-8">
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle className="font-merriweather text-2xl">Our Mission</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground leading-relaxed">
                Section Sense revolutionizes legal research by providing an intelligent tool that helps legal professionals, law students, and judges quickly map case descriptions to the most relevant sections of Indian law. Using advanced AI-powered semantic matching, our platform analyzes your case description and instantly identifies applicable sections under the Bharatiya Nyaya Sanhita (BNS), Bharatiya Nagarik Suraksha Sanhita (BNSS), and Bharatiya Sakshya Adhiniyam (BSA).
              </p>
            </CardContent>
          </Card>

          <Card className="shadow-card">
            <CardHeader>
              <CardTitle className="font-merriweather text-2xl">How It Works</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-semibold">1</div>
                  <div>
                    <h4 className="font-semibold text-foreground">Describe Your Case</h4>
                    <p className="text-muted-foreground">Enter a detailed description of your legal scenario or case facts.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-semibold">2</div>
                  <div>
                    <h4 className="font-semibold text-foreground">AI Analysis</h4>
                    <p className="text-muted-foreground">Our AI analyzes the semantic meaning and identifies relevant legal concepts.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-semibold">3</div>
                  <div>
                    <h4 className="font-semibold text-foreground">Get Results</h4>
                    <p className="text-muted-foreground">Receive precise legal sections with descriptions and relevant keywords.</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid md:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="shadow-card hover:shadow-elevated transition-shadow duration-300">
                <CardHeader className="text-center">
                  <feature.icon className="h-12 w-12 text-primary mx-auto mb-4" />
                  <CardTitle className="font-merriweather">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-center">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;