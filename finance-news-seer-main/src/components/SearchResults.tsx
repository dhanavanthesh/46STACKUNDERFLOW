import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowUpRight, ArrowDownRight, Calendar, RefreshCw, ExternalLink, BarChart2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useToast } from "@/components/ui/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";

// API endpoints
const API_BASE_URL = 'http://localhost:5000/api';

// API Response Types
interface ApiResponse {
  success: boolean;
  message?: string;
  timestamp: string;
}

interface NewsAnalysis {
  sentimentSummary: {
    overall: string;
    score: number;
    distribution: Record<string, number>;
  };
  topTopics: Array<{ name: string; count: number }>;
  newsItems: NewsItem[];
}

interface MarketContext {
  name: string;
  change: number;
  direction: 'up' | 'down';
  price: number;
}

interface StockAnalysisResponse extends ApiResponse {
  ticker: string;
  companyInfo: {
    name: string;
    ticker: string;
    sector: string;
    industry: string;
    website: string;
    description: string;
    country: string;
    exchange: string;
    marketCap: number;
    peRatio: number;
    beta: number;
  };
  priceInfo: {
    current: number;
    open: number;
    high: number;
    low: number;
    change: number;
    changePercent: number;
    direction: 'up' | 'down';
  };
  volumeInfo: {
    current: number;
    average: number;
    change: number;
    changePercent: number;
  };
  marketContext: MarketContext[];
  explanation: string;
  newsAnalysis: NewsAnalysis;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  correlation: any;
}

const api = {
  async analyzeStock(ticker: string): Promise<StockAnalysisResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/analyze/${ticker}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  async processQuery(query: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  async trackStocks(tickers: string[]) {
    try {
      const response = await fetch(`${API_BASE_URL}/track`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tickers })
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
};

interface FinancialItem {
  id: string;
  name: string;
  type: string;
  sector: string;
  performance: number;
  changePercent: number;
  price?: number;
  nav?: number;
  ticker?: string;
  volume?: number;
  marketCap?: number;
  beta?: number;
  holdings?: Array<{ stockName: string; percentage: number }>;
  isin?: string;
}

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  content: string;
  url: string;
  source: string;
  date: string;
  sentiment: string;
  sentimentScore: number;
  impact: string;
  entities: string[];
}

interface MarketData {
  marketIndices: Array<{
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
    direction: 'up' | 'down';
  }>;
  sectorPerformance: Array<{
    symbol: string;
    sector: string;
    price: number;
    change: number;
    changePercent: number;
    direction: 'up' | 'down';
  }>;
  marketNews: NewsItem[];
  newsSentiment: {
    overall: string;
    score: number;
    distribution: Record<string, number>;
  };
  marketAnalysis: string;
  topics: Array<{ name: string; count: number }>;
}
interface SearchResultsProps {
  query: string;
  results: FinancialItem[];
  isLoading: boolean;
}

const SearchResults = ({ query, results, isLoading }: SearchResultsProps) => {
  const [relatedNews, setRelatedNews] = useState<NewsItem[]>([]);
  const [explanations, setExplanations] = useState<Record<string, string>>({});
  const [newsLoading, setNewsLoading] = useState<boolean>(true);
  const [explanationLoading, setExplanationLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<string>("analysis");
  const [refreshing, setRefreshing] = useState<Record<string, boolean>>({});
  const { toast } = useToast();

  // Current time in UTC
  const [currentTime, setCurrentTime] = useState<string>("");
  const [currentUser] = useState<string>("Harsha2318");

  useEffect(() => {
    // Update current time
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toISOString().split('.')[0].replace('T', ' '));
    };
    
    updateTime();
    const timer = setInterval(updateTime, 1000);
    
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      if (!query) return;
  
      setNewsLoading(true);
      setExplanationLoading(true);
  
      try {
        const response = await api.processQuery(query);
        console.log('API Response:', response); // Debug log
  
        if (response.success) {
          // Set news and explanations based on response type
          if (response.marketIndices) {
            setRelatedNews(response.marketNews || []);
            setExplanations({ market: response.marketAnalysis });
            // You might want to update a market data state here
          } else if (response.ticker) {
            setRelatedNews(response.newsAnalysis.newsItems || []);
            setExplanations({ [response.ticker]: response.explanation });
          }
  
          toast({
            title: "Analysis complete",
            description: "Market data and news have been updated.",
            variant: "default",
          });
        } else {
          throw new Error(response.message);
        }
      } catch (error) {
        console.error("Failed to fetch data:", error);
        toast({
          title: "Error",
          description: "Failed to analyze market data. Please try again.",
          variant: "destructive",
        });
      } finally {
        setNewsLoading(false);
        setExplanationLoading(false);
      }
    };
  
    fetchData();
  }, [query, toast]);

  const getDisplayValue = (value: any, type: string, formatter?: (val: any) => string) => {
    if (value === undefined || value === null) return 'N/A';
    if (formatter) return formatter(value);
    return String(value);
  };

  const handleRefresh = async (itemId: string, itemName: string) => {
    setRefreshing(prev => ({ ...prev, [itemId]: true }));
    
    try {
      const response = await api.analyzeStock(itemName);
      
      if (response.success) {
        setRelatedNews(prev => {
          const filteredNews = prev.filter(n => !n.entities.includes(itemName));
          return [...filteredNews, ...(response.newsAnalysis.newsItems || [])];
        });
        
        setExplanations(prev => ({
          ...prev,
          [itemId]: response.explanation
        }));
        
        toast({
          title: "Refreshed successfully",
          description: `Latest data for ${itemName} has been loaded.`,
          variant: "default",
        });
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      console.error("Failed to refresh data:", error);
      toast({
        title: "Refresh failed",
        description: "Could not update the information. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setRefreshing(prev => ({ ...prev, [itemId]: false }));
    }
  };

  if (isLoading) {
    return <div className="animate-pulse">Loading...</div>;
  }

  if (results.length === 0) {
    return (
      <div className="py-12 text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">No Results Found</h2>
        <p className="text-gray-600">
          We couldn't find any financial instruments matching your query.
          <br />
          Try a different search term.
        </p>
      </div>
    );
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case "positive":
        return "bg-green-100 text-green-800";
      case "negative":
        return "bg-red-100 text-red-800";
      case "neutral":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-blue-100 text-blue-800";
    }
  };

  const getImpactBadge = (impact: string) => {
    switch (impact?.toLowerCase()) {
      case "high":
        return <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">High Impact</Badge>;
      case "medium":
        return <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">Medium Impact</Badge>;
      case "low":
        return <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">Low Impact</Badge>;
      default:
        return null;
    }
  };


  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2 flex items-center">
          Results for: <span className="text-blue-600 ml-2">"{query}"</span>
        </h2>
        <div className="text-sm text-gray-600">
          <div>Current Date and Time (UTC): {currentTime}</div>
          <div>Current User's Login: {currentUser}</div>
        </div>
      </div>
  
      {/* Market Analysis */}
      {explanations.market && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Market Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm">
                {explanations.market}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}
  
      {/* Market News */}
      {relatedNews.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Latest Market News</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[400px]">
              <div className="space-y-4">
                {relatedNews.map((news) => (
                  <div key={news.id} className="border-b pb-4">
                    <h3 className="font-medium mb-1">{news.title}</h3>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <span>{news.source}</span>
                      <span>•</span>
                      <span>{news.date}</span>
                      <Badge className={getSentimentColor(news.sentiment)}>
                        {news.sentiment}
                      </Badge>
                    </div>
                    {news.summary && (
                      <p className="mt-2 text-sm text-gray-700">{news.summary}</p>
                    )}
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SearchResults;
