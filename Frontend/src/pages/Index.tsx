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

        {/* Modern Search Section */}
        <div className="relative mb-8">
          {/* Background Decorations */}
          <div className="absolute -top-32 -left-32 w-96 h-96 bg-primary/10 rounded-full blur-3xl opacity-50 pointer-events-none" />
          <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl opacity-50 pointer-events-none" />
          
          <Card className="relative shadow-2xl border-2 border-primary/30 backdrop-blur-sm bg-card/95 overflow-hidden">
            {/* Animated gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-blue-500/5 to-primary/5 animate-pulse pointer-events-none" />
            
            <CardContent className="p-8 lg:p-12 relative">
              {/* Search Mode Tabs */}
              <div className="flex justify-center mb-10">
                <div className="inline-flex items-center gap-2 p-1.5 bg-muted/50 backdrop-blur-sm rounded-full border border-border/50">
                  <Button 
                    variant={searchMode === 'simple' ? 'default' : 'ghost'}
                    size="lg"
                    onClick={() => setSearchMode('simple')}
                    className={`rounded-full px-8 transition-all ${searchMode === 'simple' ? 'shadow-lg' : ''}`}
                  >
                    <Search className="h-4 w-4 mr-2" />
                    Natural Language
                  </Button>
                  <Button 
                    variant={searchMode === 'advanced' ? 'default' : 'ghost'}
                    size="lg"
                    onClick={() => setSearchMode('advanced')}
                    className={`rounded-full px-8 transition-all ${searchMode === 'advanced' ? 'shadow-lg' : ''}`}
                  >
                    <Filter className="h-4 w-4 mr-2" />
                    Precise Search
                  </Button>
                </div>
              </div>

              {/* Simple Search Mode */}
              {searchMode === 'simple' && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
                  <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-primary via-blue-500 to-primary rounded-2xl blur opacity-20 group-hover:opacity-30 transition duration-300" />
                    <div className="relative">
                      <Textarea 
                        placeholder="Ask your legal question naturally... Try: 'What happens if someone steals property worth 10 lakhs?' or 'Tell me about bail provisions for non-bailable offenses'"
                        value={query} 
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => { if (e.key === 'Enter' && e.ctrlKey) { handleSearch(); } }}
                        rows={6} 
                        className="resize-none text-lg border-2 border-primary/20 focus:border-primary bg-background/95 backdrop-blur-sm shadow-inner rounded-2xl p-6 transition-all" 
                      />
                      <div className="absolute bottom-4 right-4 flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">
                          <Sparkles className="h-3 w-3 mr-1" />
                          AI-Powered
                        </Badge>
                        <span className="text-xs text-muted-foreground">Ctrl+Enter</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Advanced Search Mode */}
              {searchMode === 'advanced' && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
                  {/* Search Type Toggle */}
                  <div className="flex justify-center">
                    <div className="inline-flex items-center gap-1 p-1 bg-muted/30 rounded-xl border border-border/50">
                      <Button 
                        variant={searchType === 'semantic' ? 'default' : 'ghost'}
                        size="sm"
                        onClick={() => setSearchType('semantic')}
                        className="rounded-lg px-4"
                      >
                        <Sparkles className="h-3.5 w-3.5 mr-1.5" />
                        Semantic
                      </Button>
                      <Button 
                        variant={searchType === 'keyword' ? 'default' : 'ghost'}
                        size="sm"
                        onClick={() => setSearchType('keyword')}
                        className="rounded-lg px-4"
                      >
                        <Filter className="h-3.5 w-3.5 mr-1.5" />
                        Keyword
                      </Button>
                    </div>
                  </div>
                  
                  {/* Search Input */}
                  <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-primary via-blue-500 to-primary rounded-2xl blur opacity-20 group-hover:opacity-30 transition duration-300" />
                    <div className="relative flex items-center">
                      <Search className="absolute left-5 h-5 w-5 text-muted-foreground pointer-events-none" />
                      <Input 
                        placeholder="BNS-302, Section 420, theft, murder..." 
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => { if (e.key === 'Enter') { handleSearch(); } }}
                        className="pl-14 pr-6 h-16 text-lg border-2 border-primary/20 focus:border-primary bg-background/95 backdrop-blur-sm shadow-inner rounded-2xl transition-all" 
                      />
                    </div>
                  </div>
                </div>
              )}
              
              {/* Search Button */}
              <div className="flex justify-center mt-10">
                <Button 
                  onClick={handleSearch} 
                  disabled={!query.trim() || isLoading}
                  size="lg" 
                  className="relative group bg-gradient-to-r from-primary via-primary to-blue-600 hover:from-primary/90 hover:via-primary/90 hover:to-blue-600/90 text-primary-foreground px-16 h-16 text-xl font-bold shadow-2xl hover:shadow-primary/50 transition-all duration-300 rounded-2xl overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                  {isLoading ? (
                    <>
                      <Loader2 className="h-6 w-6 mr-3 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="h-6 w-6 mr-3" />
                      Search Legal Database
                    </>
                  )}
                </Button>
              </div>

              {/* Quick Search Pills */}
              <div className="mt-12 p-8 bg-gradient-to-br from-primary/5 via-blue-500/5 to-primary/5 rounded-2xl border border-primary/10 backdrop-blur-sm">
                <div className="flex items-center justify-center gap-2 mb-5">
                  <div className="p-2 bg-primary/10 rounded-full">
                    <TrendingUp className="h-5 w-5 text-primary" />
                  </div>
                  <p className="text-lg font-bold text-foreground">Trending Searches</p>
                </div>
                <div className="flex flex-wrap justify-center gap-3">
                  {quickSearchTerms.map((term) => (
                    <Button 
                      key={term} 
                      variant="outline" 
                      size="default"
                      onClick={() => handleQuickSearch(term)} 
                      disabled={isLoading}
                      className="text-sm font-medium hover:bg-primary hover:text-primary-foreground hover:border-primary transition-all hover:scale-105 shadow-md hover:shadow-lg rounded-full px-5 py-2"
                    >
                      {term}
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

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
