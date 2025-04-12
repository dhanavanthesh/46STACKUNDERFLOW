
import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { NewsItem } from "@/types";
import { Badge } from "@/components/ui/badge";
import { fetchLatestNews } from "@/utils/newsUtils";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import LoadingState from "@/components/LoadingState";

const NewsView = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [category, setCategory] = useState<string>("all");
  
  useEffect(() => {
    const loadNews = async () => {
      setIsLoading(true);
      try {
        const newsData = await fetchLatestNews(category !== "all" ? category : undefined);
        setNews(newsData);
      } catch (error) {
        console.error("Failed to load news:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadNews();
  }, [category]);

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
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

  if (isLoading) {
    return <LoadingState />;
  }

  return (
    <div className="space-y-4">
      <Tabs defaultValue="all" value={category} onValueChange={setCategory}>
        <TabsList>
          <TabsTrigger value="all">All News</TabsTrigger>
          <TabsTrigger value="markets">Markets</TabsTrigger>
          <TabsTrigger value="economy">Economy</TabsTrigger>
          <TabsTrigger value="companies">Companies</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {news.map((item) => (
          <Card key={item.id} className="overflow-hidden">
            <CardHeader className="pb-2">
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg">{item.title}</CardTitle>
                <Badge className={cn("ml-2", getSentimentColor(item.sentiment))}>
                  {item.sentiment}
                </Badge>
              </div>
              <CardDescription className="flex items-center justify-between">
                <span>Source: {item.source}</span>
                <span>{new Date(item.date).toLocaleDateString()}</span>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700">{item.summary}</p>
              <div className="mt-2 flex flex-wrap gap-1">
                {item.entities.map((entity, i) => (
                  <Badge key={i} variant="outline" className="bg-blue-50">
                    {entity}
                  </Badge>
                ))}
              </div>
            </CardContent>
            <CardFooter className="pt-2 border-t bg-gray-50">
              <div className="w-full flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  Impact: <span className="font-medium">{item.impact}</span>
                </div>
                <a 
                  href={item.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Read Full Article
                </a>
              </div>
            </CardFooter>
          </Card>
        ))}
      </div>
      
      {news.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-600">No news articles found for this category</h3>
          <p className="text-gray-500">Try selecting a different category or check back later</p>
        </div>
      )}
    </div>
  );
};

export default NewsView;
