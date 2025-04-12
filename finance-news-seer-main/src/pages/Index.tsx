
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import DashboardView from "@/components/DashboardView";
import NewsView from "@/components/NewsView";
import SearchResults from "@/components/SearchResults";
import FinancialChatbot from "@/components/FinancialChatbot";
import { searchFinancialData } from "@/utils/searchUtils";
import { fetchMutualFundsData, fetchStocksData } from "@/utils/dataUtils";
import { FinancialItem, NewsItem } from "@/types";
import LoadingState from "@/components/LoadingState";

const Index = () => {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searchResults, setSearchResults] = useState<FinancialItem[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const [mutualFunds, setMutualFunds] = useState<FinancialItem[]>([]);
  const [stocks, setStocks] = useState<FinancialItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  
  const { toast } = useToast();

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const fundsData = await fetchMutualFundsData();
        const stocksData = await fetchStocksData();
        
        setMutualFunds(fundsData);
        setStocks(stocksData);
        setIsLoading(false);
      } catch (error) {
        console.error("Failed to load initial data:", error);
        toast({
          title: "Error Loading Data",
          description: "Failed to load financial data. Please try again later.",
          variant: "destructive"
        });
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, [toast]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast({
        title: "Empty Search",
        description: "Please enter a search query",
        variant: "destructive"
      });
      return;
    }

    setIsSearching(true);
    setHasSearched(true);
    
    try {
      const results = await searchFinancialData(searchQuery, [...mutualFunds, ...stocks]);
      setSearchResults(results);
      
      if (results.length === 0) {
        toast({
          title: "No Results",
          description: "No matching financial instruments found",
          variant: "default"
        });
      }
      
      // Switch to search results tab
      setActiveTab("search");
    } catch (error) {
      console.error("Search error:", error);
      toast({
        title: "Search Failed",
        description: "An error occurred while searching. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSearching(false);
    }
  };

  if (isLoading) {
    return <LoadingState />;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto py-4 px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <h1 className="text-2xl font-bold text-blue-600">News Sense</h1>
            <div className="w-full md:w-1/2 flex gap-2">
              <Input
                placeholder="e.g., 'Why did Jyothy Labs up today?' or 'What happened to Nifty this week?'"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    handleSearch();
                  }
                }}
                className="flex-1"
              />
              <Button 
                onClick={handleSearch} 
                disabled={isSearching}
              >
                {isSearching ? "Searching..." : "Search"}
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto flex-1 p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-4 mb-4">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="news">Latest News</TabsTrigger>
            <TabsTrigger value="chatbot">Financial Assistant</TabsTrigger>
            <TabsTrigger value="search" disabled={!hasSearched}>
              Search Results
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="dashboard">
            <DashboardView mutualFunds={mutualFunds} stocks={stocks} />
          </TabsContent>
          
          <TabsContent value="news">
            <NewsView />
          </TabsContent>
          
          <TabsContent value="chatbot">
            <FinancialChatbot financialItems={[...stocks, ...mutualFunds]} />
          </TabsContent>
          
          <TabsContent value="search">
            {hasSearched && (
              <SearchResults 
                query={searchQuery} 
                results={searchResults}
                isLoading={isSearching}
              />
            )}
          </TabsContent>
        </Tabs>
      </main>
      
      <footer className="bg-white border-t py-4">
        <div className="container mx-auto px-4 text-center text-gray-500">
          <p>© 2025 News Sense - Financial News Analysis</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
