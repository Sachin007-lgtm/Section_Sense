import { LawSectionResponse } from '@/services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Clock, 
  Scale, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  BookOpen,
  Star,
  Copy,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Brain,
  MessageCircle
} from 'lucide-react';
import { useState } from 'react';
import { useToast } from '@/hooks/use-toast';
import { useExplanation } from '@/hooks/useExplanation';
import ExplanationDisplay from '@/components/ExplanationDisplay';
import ChatGPTChatbot from '@/components/ChatGPTChatbot';

interface SearchResultsProps {
  results: LawSectionResponse[];
  query: string;
  totalResults?: number;
  executionTime?: number;
}

const SearchResults = ({ results, query, totalResults, executionTime }: SearchResultsProps) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [explanations, setExplanations] = useState<Record<string, any>>({}); // Store explanations by section code
  const [chatbotOpen, setChatbotOpen] = useState(false);
  const [sectionContext, setSectionContext] = useState<{code: string; title: string; description: string} | undefined>();
  const { toast } = useToast();
  const { generateExplanation, isLoading: explanationLoading } = useExplanation();

  const toggleExpanded = (sectionCode: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionCode)) {
      newExpanded.delete(sectionCode);
    } else {
      newExpanded.add(sectionCode);
    }
    setExpandedSections(newExpanded);
  };

  const toggleExplanation = async (section: LawSectionResponse) => {
    const sectionCode = section.section_code;
    
    if (explanations[sectionCode]) {
      // Remove explanation if it exists
      const newExplanations = { ...explanations };
      delete newExplanations[sectionCode];
      setExplanations(newExplanations);
    } else {
      // Generate explanation if not already shown
      const explanation = await generateExplanation({
        section_code: section.section_code,
        section_text: section.description || '',
        context: query,
        user_type: 'general',
        explanation_style: 'simple'
      });
      
      if (explanation) {
        setExplanations(prev => ({
          ...prev,
          [sectionCode]: explanation
        }));
      }
    }
  };

  const getViewSourceUrl = (section: LawSectionResponse) => {
    // Create a more specific URL for Indian legal sources
    const sectionCode = section.section_code;
    const sectionNumber = section.section_number;
    
    // If there's already a specific source URL, use it
    if (section.source && section.source !== 'https://www.indiacode.nic.in' && section.source.includes('http')) {
      return section.source;
    }
    
    // Build specific URLs based on the act type
    if (sectionCode.includes('BNS') || sectionCode.startsWith('3')) {
      // Bharatiya Nyaya Sanhita - try to construct a specific URL
      return `https://www.indiacode.nic.in/show-data?actid=AC_CEN_5_6_00037_202312_1704179233074&sectionId=&sectionno=${sectionNumber}&orderno=`;
    } else if (sectionCode.includes('BNSS') || sectionCode.startsWith('1')) {
      // Bharatiya Nagarik Suraksha Sanhita
      return `https://www.indiacode.nic.in/show-data?actid=AC_CEN_5_6_00038_202312_1704179355834&sectionId=&sectionno=${sectionNumber}&orderno=`;
    } else if (sectionCode.includes('BSA') || sectionCode.startsWith('2')) {
      // Bharatiya Sakshya Adhiniyam
      return `https://www.indiacode.nic.in/show-data?actid=AC_CEN_5_6_00039_202312_1704179581370&sectionId=&sectionno=${sectionNumber}&orderno=`;
    }
    
    // Fallback to general search on India Code
    return `https://www.indiacode.nic.in/search?q=${encodeURIComponent(section.title)}`;
  };

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: "Copied to clipboard",
        description: `${label} has been copied to your clipboard.`,
      });
    } catch (err) {
      toast({
        title: "Copy failed",
        description: "Could not copy to clipboard. Please try again.",
        variant: "destructive",
      });
    }
  };

  const getActColor = (sectionCode: string) => {
    if (sectionCode.includes('BNS') || sectionCode.startsWith('3')) {
      return 'bg-primary text-primary-foreground';
    } else if (sectionCode.includes('BNSS') || sectionCode.startsWith('1')) {
      return 'bg-secondary text-secondary-foreground';
    } else if (sectionCode.includes('BSA') || sectionCode.startsWith('2')) {
      return 'bg-justice-gold text-justice-gold-foreground';
    }
    return 'bg-muted text-muted-foreground';
  };

  const getActName = (sectionCode: string) => {
    if (sectionCode.includes('BNS') || sectionCode.startsWith('3')) {
      return 'Bharatiya Nyaya Sanhita';
    } else if (sectionCode.includes('BNSS') || sectionCode.startsWith('1')) {
      return 'Bharatiya Nagarik Suraksha Sanhita';
    } else if (sectionCode.includes('BSA') || sectionCode.startsWith('2')) {
      return 'Bharatiya Sakshya Adhiniyam';
    }
    return 'Criminal Law';
  };

  const getBailableIcon = (bailable: string | undefined) => {
    if (bailable === 'Yes' || bailable === 'true') {
      return <CheckCircle className="h-4 w-4 text-green-600" />;
    } else if (bailable === 'No' || bailable === 'false') {
      return <XCircle className="h-4 w-4 text-red-600" />;
    }
    return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
  };

  const getCognizableIcon = (cognizable: string | undefined) => {
    if (cognizable === 'Yes' || cognizable === 'true') {
      return <CheckCircle className="h-4 w-4 text-green-600" />;
    } else if (cognizable === 'No' || cognizable === 'false') {
      return <XCircle className="h-4 w-4 text-red-600" />;
    }
    return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
  };

  const getSeverityColor = (category: string) => {
    const lowerCategory = category?.toLowerCase() || '';
    if (lowerCategory.includes('murder') || lowerCategory.includes('death') || lowerCategory.includes('heinous')) {
      return 'bg-orange-100 text-orange-800 border-orange-200';
    } else if (lowerCategory.includes('theft') || lowerCategory.includes('property') || lowerCategory.includes('fraud')) {
      return 'bg-blue-100 text-blue-800 border-blue-200';
    } else if (lowerCategory.includes('assault') || lowerCategory.includes('hurt') || lowerCategory.includes('human body')) {
      return 'bg-amber-100 text-amber-800 border-amber-200';
    } else if (lowerCategory.includes('document') || lowerCategory.includes('forgery')) {
      return 'bg-purple-100 text-purple-800 border-purple-200';
    }
    return 'bg-success/10 text-success border-success/20';
  };

  if (results.length === 0) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <Scale className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-foreground mb-2">No sections found</h3>
        <p className="text-muted-foreground">
          Try rephrasing your query or using more general terms.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search Summary */}
      <div className="card-enhanced rounded-lg p-4 animate-fade-in">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h2 className="font-merriweather text-xl font-semibold text-foreground">
              Search Results for "<span className="text-primary font-semibold">{query}</span>"
            </h2>
            <p className="text-muted-foreground">
              Found {totalResults || results.length} relevant legal sections
              {executionTime && (
                <span className="inline-flex items-center ml-2 text-success">
                  <Clock className="h-4 w-4 mr-1" />
                  {(executionTime * 1000).toFixed(0)}ms
                </span>
              )}
            </p>
          </div>
          <Badge variant="secondary" className="bg-gradient-justice text-justice-gold-foreground shadow-sm">
            {results.length} shown
          </Badge>
        </div>
      </div>

      {/* Results List */}
      <div className="space-y-4">
        {results.map((section, index) => {
          const isExpanded = expandedSections.has(section.section_code);
          const hasExplanation = !!explanations[section.section_code];
          const similarityScore = (section as any).similarity_score;
          
          return (
            <Card key={section.section_code || index} className="card-enhanced hover:shadow-glow transition-all duration-300 hover:scale-[1.02] animate-fade-in group">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <Badge className={`${getActColor(section.section_code)} shadow-sm`}>
                        {getActName(section.section_code)}
                      </Badge>
                      <Badge variant="outline" className="font-mono text-sm border-primary/30">
                        Section {section.section_number}
                      </Badge>
                      {similarityScore && (
                        <Badge variant="secondary" className="bg-success/10 text-success border-success/20">
                          <Star className="h-3 w-3 mr-1 fill-current" />
                          {(similarityScore * 100).toFixed(0)}% match
                        </Badge>
                      )}
                    </div>
                    <CardTitle className="font-merriweather text-lg font-semibold leading-tight">
                      {section.title}
                    </CardTitle>
                    <CardDescription className="mt-2">
                      {isExpanded ? section.description : 
                        section.description?.length > 200 ? 
                        `${section.description.substring(0, 200)}...` : 
                        section.description
                      }
                    </CardDescription>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(
                      `${section.section_code}: ${section.title}\n\n${section.description}`,
                      'Section details'
                    )}
                    className="hover:bg-primary/10 hover:text-primary transition-all duration-200"
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>

                {/* Category Badge */}
                {section.category && (
                  <Badge className={`w-fit ${getSeverityColor(section.category)}`}>
                    <BookOpen className="h-3 w-3 mr-1" />
                    {section.category}
                  </Badge>
                )}
              </CardHeader>

              <CardContent className="pt-0">
                {/* Quick Info Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  {section.bailable && (
                    <div className="flex items-center gap-2 text-sm">
                      {getBailableIcon(section.bailable)}
                      <span className="text-muted-foreground">
                        Bailable: <span className="font-medium">{section.bailable}</span>
                      </span>
                    </div>
                  )}
                  {section.cognizable && (
                    <div className="flex items-center gap-2 text-sm">
                      {getCognizableIcon(section.cognizable)}
                      <span className="text-muted-foreground">
                        Cognizable: <span className="font-medium">{section.cognizable}</span>
                      </span>
                    </div>
                  )}
                  {section.compoundable && (
                    <div className="flex items-center gap-2 text-sm">
                      <AlertTriangle className="h-4 w-4 text-yellow-600" />
                      <span className="text-muted-foreground">
                        Compoundable: <span className="font-medium">{section.compoundable}</span>
                      </span>
                    </div>
                  )}
                </div>

                {/* Punishment Details */}
                {(section.punishment || section.fine_range || section.imprisonment_range) && (
                  <div className="bg-gradient-to-r from-success/5 to-success/10 border border-success/20 rounded-md p-3 mb-4">
                    <h4 className="font-medium text-sm text-success mb-2 flex items-center">
                      <Scale className="h-4 w-4 mr-1" />
                      Punishment Details
                    </h4>
                    <div className="space-y-1 text-sm text-success">
                      {section.punishment && (
                        <p><span className="font-medium">Punishment:</span> {section.punishment}</p>
                      )}
                      {section.imprisonment_range && (
                        <p><span className="font-medium">Imprisonment:</span> {section.imprisonment_range}</p>
                      )}
                      {section.fine_range && (
                        <p><span className="font-medium">Fine:</span> {section.fine_range}</p>
                      )}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center justify-between pt-2 flex-wrap gap-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Button
                      variant={hasExplanation ? "default" : "outline"}
                      size="sm"
                      onClick={() => toggleExplanation(section)}
                      disabled={explanationLoading}
                      className="transition-all duration-200"
                    >
                      <Brain className="h-4 w-4 mr-1" />
                      {hasExplanation ? 'Hide' : 'Explain'}
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSectionContext({
                          code: section.section_code,
                          title: section.title,
                          description: section.description
                        });
                        setChatbotOpen(true);
                      }}
                      className="transition-all duration-200 hover:bg-primary/10 hover:text-primary"
                    >
                      <MessageCircle className="h-4 w-4 mr-1" />
                      Ask Kamado
                    </Button>
                  </div>
                  
                  {section.source && (
                    <Button
                      variant="outline"
                      size="sm"
                      asChild
                    >
                      <a
                        href={getViewSourceUrl(section)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center"
                      >
                        <ExternalLink className="h-4 w-4 mr-1" />
                        View Source
                      </a>
                    </Button>
                  )}
                </div>

                {/* Explanation Display */}
                {hasExplanation && (
                  <div className="mt-4">
                    <ExplanationDisplay 
                      explanation={explanations[section.section_code]}
                      onClose={() => {
                        const newExplanations = { ...explanations };
                        delete newExplanations[section.section_code];
                        setExplanations(newExplanations);
                      }}
                    />
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Footer Note */}
      <div className="text-center text-sm text-muted-foreground pt-6 border-t">
        <p className="flex items-center justify-center gap-2">
          <AlertTriangle className="h-4 w-4" />
          This is an AI-powered search system. Please verify all legal references independently.
        </p>
      </div>
      
      {/* Chatbot */}
      <ChatGPTChatbot 
        isOpen={chatbotOpen} 
        onClose={() => {
          setChatbotOpen(false);
          setSectionContext(undefined);
        }} 
        sectionContext={sectionContext}
      />
    </div>
  );
};

export default SearchResults;