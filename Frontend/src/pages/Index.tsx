import { useState } from 'react';
import { Search, Sparkles, Filter, Loader2, Scale, BookOpen, FileText, TrendingUp, Clock, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import SearchResults from '@/components/SearchResults';
import { useSearch } from '@/hooks/useSearch';

const Index = () => {
  const [query, setQuery] = useState('');
  const [searchMode, setSearchMode] = useState('simple');
  const [searchType, setSearchType] = useState('semantic');
  
  const { results, isLoading, error, search, clearResults, clearError } = useSearch({
    searchType: 'section_search',
    maxResults: 20,
  });

  const handleSearch = async () => {
    if (!query.trim()) return;
    await search(query);
  };

  const handleQuickSearch = (searchTerm) => {
    setQuery(searchTerm);
    search(searchTerm);
  };

  const quickSearchTerms = [
    'theft and robbery', 'murder and culpable homicide', 'assault and hurt', 
    'fraud and cheating', 'cybercrime', 'domestic violence', 
    'property crimes', 'evidence admissibility', 'bail provisions'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Hero Section */}
        <div className="text-center mb-12 space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 dark:bg-primary/20 rounded-full mb-4">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">AI-Powered Legal Search</span>
          </div>
          <h1 className="text-5xl font-bold mb-4 leading-tight pb-2 bg-gradient-to-r from-foreground to-primary bg-clip-text text-transparent">
            Legal Section Search
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Search through BNS, BNSS, and BSA with precision and speed
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="border-l-4 border-l-primary/70 hover:shadow-lg transition-shadow">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="p-3 bg-primary/10 rounded-lg">
                <BookOpen className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">3</p>
                <p className="text-sm text-muted-foreground">Legal Acts Covered</p>
              </div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-blue-500/70 hover:shadow-lg transition-shadow">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="p-3 bg-blue-500/10 rounded-lg">
                <FileText className="h-6 w-6 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">1000+</p>
                <p className="text-sm text-muted-foreground">Sections Indexed</p>
              </div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-green-500/70 hover:shadow-lg transition-shadow">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="p-3 bg-green-500/10 rounded-lg">
                <Zap className="h-6 w-6 text-green-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">&lt;1s</p>
                <p className="text-sm text-muted-foreground">Average Response Time</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search Card */}
        <Card className="shadow-2xl border-2 border-primary/20 mb-8 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-primary/5 pointer-events-none" />
          <CardContent className="p-8 relative">
            <Tabs value={searchMode} onValueChange={(value) => setSearchMode(value)}>
              <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8 h-12">
                <TabsTrigger value="simple" className="text-base">
                  <Search className="h-4 w-4 mr-2" />
                  Simple Search
                </TabsTrigger>
                <TabsTrigger value="advanced" className="text-base">
                  <Filter className="h-4 w-4 mr-2" />
                  Advanced Search
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="simple" className="space-y-4">
                <div className="relative">
                  <Textarea 
                    placeholder="Describe your case or legal scenario... (e.g., 'What are the provisions for theft of property worth more than 5 lakhs?')"
                    value={query} 
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter' && e.ctrlKey) { handleSearch(); } }}
                    rows={5} 
                    className="resize-none text-base border-2 focus:border-primary transition-colors" 
                  />
                  <div className="absolute bottom-3 right-3 text-xs text-muted-foreground">
                    Press Ctrl+Enter to search
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="advanced" className="space-y-6">
                <div className="flex justify-center mb-6">
                  <Tabs value={searchType} onValueChange={(value) => setSearchType(value)}>
                    <TabsList className="grid w-fit grid-cols-2 h-11">
                      <TabsTrigger value="semantic" className="text-sm">
                        <Sparkles className="h-4 w-4 mr-2" />
                        Semantic
                      </TabsTrigger>
                      <TabsTrigger value="keyword" className="text-sm">
                        <Filter className="h-4 w-4 mr-2" />
                        Keyword
                      </TabsTrigger>
                    </TabsList>
                  </Tabs>
                </div>
                <Input 
                  placeholder="Enter specific legal terms or section numbers..." 
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') { handleSearch(); } }}
                  className="text-base h-12 border-2 focus:border-primary transition-colors" 
                />
              </TabsContent>
              
              <div className="flex justify-center mt-8">
                <Button 
                  onClick={handleSearch} 
                  disabled={!query.trim() || isLoading}
                  size="lg" 
                  className="bg-primary hover:bg-primary/90 text-primary-foreground px-12 h-14 text-lg font-semibold shadow-lg hover:shadow-xl transition-all hover:scale-105"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="h-5 w-5 mr-2" />
                      Find Sections
                    </>
                  )}
                </Button>
              </div>
            </Tabs>

            {/* Quick Search Section */}
            <div className="mt-10 p-6 bg-gradient-to-r from-primary/5 via-primary/10 to-primary/5 rounded-xl border border-primary/20">
              <div className="flex items-center justify-center gap-2 mb-4">
                <TrendingUp className="h-5 w-5 text-primary" />
                <p className="text-base font-semibold text-foreground">Popular Searches</p>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {quickSearchTerms.map((term) => (
                  <Button 
                    key={term} 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleQuickSearch(term)} 
                    disabled={isLoading}
                    className="text-sm hover:bg-primary hover:text-primary-foreground transition-all hover:scale-105 shadow-sm"
                  >
                    {term}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {error && (
          <Alert variant="destructive" className="mb-6 shadow-lg border-2">
            <AlertDescription className="flex items-center justify-between">
              <span className="font-medium">{error}</span>
              <Button variant="ghost" size="sm" onClick={clearError} className="hover:bg-destructive/20">
                Dismiss
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {results && results.results.length > 0 && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between mb-6 p-4 bg-gradient-to-r from-green-500/10 to-green-500/5 rounded-lg border border-green-500/20">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-500/20 rounded-full">
                  <FileText className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <Badge variant="secondary" className="text-base font-semibold px-4 py-1">
                    {results.results.length} results found
                  </Badge>
                  <p className="text-xs text-muted-foreground mt-1">
                    Search completed in {results.execution_time?.toFixed(2) || '0.00'}s
                  </p>
                </div>
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={clearResults}
                className="hover:bg-destructive/10 hover:text-destructive hover:border-destructive"
              >
                Clear Results
              </Button>
            </div>
            <SearchResults results={results.results} query={query} />
          </div>
        )}

        {!isLoading && !error && (!results || results.results.length === 0) && !query && (
          <div className="text-center py-20 animate-in fade-in duration-700">
            <div className="relative inline-block mb-6">
              <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full" />
              <div className="relative p-6 bg-primary/10 rounded-full">
                <Scale className="h-20 w-20 text-primary" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-foreground mb-3">Ready to Search Legal Sections</h3>
            <p className="text-muted-foreground text-lg mb-6 max-w-md mx-auto">
              Enter your legal query above or try one of the popular searches to get started
            </p>
            <div className="flex items-center justify-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                <span>Fast Results</span>
              </div>
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                <span>AI-Powered</span>
              </div>
              <div className="flex items-center gap-2">
                <Scale className="h-4 w-4" />
                <span>Accurate</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Index;
