
import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useToast } from "@/components/ui/use-toast";
import { analyzeSentiment, generateDetailedAnalysis } from "@/utils/nlpUtils";
import { fetchRealtimeNews, scrapeFinancialNewsSites } from "@/utils/scraperUtils";
import { FinancialItem, NewsItem } from "@/types";
import { Send, Bot, User, Loader2 } from "lucide-react";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

type FinancialChatbotProps = {
  financialItems: FinancialItem[];
};

const FinancialChatbot = ({ financialItems }: FinancialChatbotProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! I can help you understand why stocks and mutual funds are performing a certain way. Ask me about any financial instrument.",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();
  const bottomRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    // Scroll to bottom whenever messages change
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isProcessing) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue.trim(),
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsProcessing(true);

    try {
      // Process user query
      const query = userMessage.content.toLowerCase();
      
      // Find mentioned financial instruments
      const matchedItems = findMentionedFinancialItems(query, financialItems);
      
      if (matchedItems.length === 0) {
        // Handle popular stocks that might not be in our dataset
        const popularStock = detectPopularStock(query);
        
        if (popularStock) {
          // Create a mock financial item for the popular stock
          const mockItem: FinancialItem = {
            id: `mock-${popularStock.id}`,
            name: popularStock.name,
            type: "Stock",
            ticker: popularStock.ticker,
            isin: "MOCK123456789",
            sector: popularStock.sector,
            performance: popularStock.performance || -1.2, // Mock negative performance as user is asking why it's down
            changePercent: -0.8, // Mock market change percentage
            holdings: []
          };
          
          // Fetch news specifically for this popular stock
          const stockNews = await fetchRealtimeNews(popularStock.name);
          
          // Generate detailed analysis for the popular stock
          const analysis = await generateDetailedAnalysis(query, mockItem, stockNews);
          
          const botResponse: Message = {
            id: Date.now().toString(),
            role: "assistant",
            content: analysis,
            timestamp: new Date(),
          };
          
          setMessages(prev => [...prev, botResponse]);
          setIsProcessing(false);
          return;
        }
        
        // No specific financial instrument mentioned and not a popular stock
        // Try to scrape general financial news
        try {
          const generalNews = await scrapeFinancialNewsSites();
          
          if (generalNews.length > 0) {
            // Provide a general market summary from scraped news
            const generalResponse: Message = {
              id: Date.now().toString(),
              role: "assistant",
              content: `I don't have specific information about the financial instrument you mentioned. However, here's some recent market news:\n\n${generalNews.slice(0, 2).map(news => `📊 **${news.title}**\n${news.summary}`).join('\n\n')}\n\nTry asking about a specific stock or mutual fund in our database for detailed analysis.`,
              timestamp: new Date(),
            };
            setMessages(prev => [...prev, generalResponse]);
          } else {
            const generalResponse: Message = {
              id: Date.now().toString(),
              role: "assistant",
              content: "I couldn't identify a specific financial instrument in your query. Try mentioning a stock name, mutual fund, or ask about a specific market sector.",
              timestamp: new Date(),
            };
            setMessages(prev => [...prev, generalResponse]);
          }
        } catch (error) {
          console.error("Error scraping general news:", error);
          const generalResponse: Message = {
            id: Date.now().toString(),
            role: "assistant",
            content: "I couldn't identify a specific financial instrument in your query. Try mentioning a stock name, mutual fund, or ask about a specific market sector.",
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, generalResponse]);
        }
        
        setIsProcessing(false);
        return;
      }
      
      // For each matched item, fetch news and analyze
      const analysisPromises = matchedItems.map(async (item) => {
        // Fetch related news for the instrument
        const relatedNews = await fetchRealtimeNews(item.name);
        
        // Generate detailed analysis
        return await generateDetailedAnalysis(query, item, relatedNews);
      });
      
      const analysisResults = await Promise.all(analysisPromises);
      
      // Combine analysis results into a response
      const responseContent = analysisResults.join("\n\n");
      
      const botResponse: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: responseContent || "I couldn't find enough information to analyze this financial instrument. Try being more specific or ask about a different stock or fund.",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, botResponse]);
      
    } catch (error) {
      console.error("Error processing query:", error);
      toast({
        title: "Analysis Error",
        description: "Failed to process your query. Please try again.",
        variant: "destructive",
      });
      
      const errorResponse: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: "I encountered an error while analyzing your query. Please try again or rephrase your question.",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsProcessing(false);
    }
  };

  const findMentionedFinancialItems = (query: string, items: FinancialItem[]): FinancialItem[] => {
    return items.filter(item => {
      const itemNameLower = item.name.toLowerCase();
      const sectorLower = item.sector.toLowerCase();
      
      return query.includes(itemNameLower) || 
             (item.ticker && query.includes(item.ticker.toLowerCase())) ||
             query.includes(sectorLower);
    });
  };

  // Detect popular stocks that might not be in our dataset
  const detectPopularStock = (query: string): { id: string, name: string, ticker: string, sector: string, performance?: number } | null => {
    const popularStocks = [
      { id: "apple", name: "Apple Inc.", ticker: "AAPL", sector: "Technology", keywords: ["apple", "aapl"] },
      { id: "microsoft", name: "Microsoft Corporation", ticker: "MSFT", sector: "Technology", keywords: ["microsoft", "msft"] },
      { id: "google", name: "Alphabet Inc.", ticker: "GOOGL", sector: "Technology", keywords: ["google", "alphabet", "googl"] },
      { id: "amazon", name: "Amazon.com Inc.", ticker: "AMZN", sector: "Consumer Cyclical", keywords: ["amazon", "amzn"] },
      { id: "tesla", name: "Tesla Inc.", ticker: "TSLA", sector: "Automotive", keywords: ["tesla", "tsla"] },
      { id: "meta", name: "Meta Platforms Inc.", ticker: "META", sector: "Technology", keywords: ["meta", "facebook", "fb"] },
      { id: "nvidia", name: "NVIDIA Corporation", ticker: "NVDA", sector: "Technology", keywords: ["nvidia", "nvda"] }
    ];

    const queryLower = query.toLowerCase();
    
    // First pass: Check if query directly mentions the stock
    for (const stock of popularStocks) {
      if (stock.keywords.some(keyword => queryLower.includes(keyword))) {
        // If the query mentions the stock is "down", "falling", etc., set a negative performance
        if (queryLower.includes("down") || queryLower.includes("fall") || queryLower.includes("drop") || queryLower.includes("decline")) {
          return { ...stock, performance: -1.5 - Math.random() * 2 }; // Random negative between -1.5 and -3.5
        }
        // If the query mentions the stock is "up", "rising", etc., set a positive performance
        else if (queryLower.includes("up") || queryLower.includes("rise") || queryLower.includes("gain") || queryLower.includes("increase")) {
          return { ...stock, performance: 1.5 + Math.random() * 2 }; // Random positive between 1.5 and 3.5
        }
        // Default case
        return stock;
      }
    }
    
    return null;
  };

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center">
          <Bot className="mr-2" size={20} />
          Financial Analysis Assistant
        </CardTitle>
        <CardDescription>
          Ask about stocks, mutual funds, or market sectors
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col h-full p-0">
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${
                  msg.role === "assistant" ? "justify-start" : "justify-end"
                }`}
              >
                <div
                  className={`flex items-start gap-2 max-w-[80%] ${
                    msg.role === "assistant" ? "flex-row" : "flex-row-reverse"
                  }`}
                >
                  <Avatar className={`h-8 w-8 ${msg.role === "assistant" ? "bg-blue-500" : "bg-gray-500"}`}>
                    {msg.role === "assistant" ? <Bot size={16} /> : <User size={16} />}
                  </Avatar>
                  <div
                    className={`rounded-lg p-3 text-sm ${
                      msg.role === "assistant"
                        ? "bg-blue-50 text-gray-800"
                        : "bg-blue-500 text-white"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    <p className="text-xs mt-1 opacity-70">
                      {msg.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
            {isProcessing && (
              <div className="flex justify-start">
                <div className="flex items-start gap-2">
                  <Avatar className="h-8 w-8 bg-blue-500">
                    <Bot size={16} />
                  </Avatar>
                  <div className="rounded-lg p-3 bg-blue-50 text-gray-800">
                    <div className="flex items-center">
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      <p>Analyzing financial data...</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </ScrollArea>
        <div className="p-3 border-t flex gap-2">
          <Input
            placeholder="Ask about market movements or specific stocks..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            disabled={isProcessing}
          />
          <Button
            onClick={handleSendMessage}
            disabled={isProcessing || !inputValue.trim()}
            className="shrink-0"
          >
            {isProcessing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default FinancialChatbot;
