
import { FinancialItem, NewsItem } from "@/types";

/**
 * Generates an explanation for why a financial instrument is performing a certain way
 * based on recent news and financial data
 * 
 * @param query The user's search query
 * @param item The financial item to explain
 * @param relatedNews News items related to the financial item
 * @returns A string explanation of the financial item's performance
 */
export const generateExplanation = async (
  query: string,
  item: FinancialItem,
  relatedNews: NewsItem[]
): Promise<string> => {
  // Simulate processing delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Default explanation if we can't determine anything specific
  let explanation = `Based on market trends, ${item.name} is currently ${
    item.performance >= 0 ? "performing well" : "underperforming"
  }.`;

  // If we have related news, use it to generate a more specific explanation
  if (relatedNews && relatedNews.length > 0) {
    // Find news with matching entities or content
    const relevantNews = relatedNews.filter(
      news => news.entities.includes(item.name) || 
             news.content.toLowerCase().includes(item.name.toLowerCase())
    );

    if (relevantNews.length > 0) {
      // Sort by impact and recency
      const sortedNews = [...relevantNews].sort((a, b) => {
        // Sort by impact first (high > medium > low)
        const impactOrder = { high: 3, medium: 2, low: 1 };
        const impactDiff = (impactOrder[b.impact] || 0) - (impactOrder[a.impact] || 0);
        
        if (impactDiff !== 0) return impactDiff;
        
        // Then sort by date (more recent first)
        return new Date(b.date).getTime() - new Date(a.date).getTime();
      });

      const mostRelevantNews = sortedNews[0];
      
      // Create an explanation based on the most relevant news
      if (mostRelevantNews) {
        const sentimentText = {
          positive: "positive",
          negative: "negative",
          neutral: "neutral",
          mixed: "mixed"
        }[mostRelevantNews.sentiment] || "mixed";

        explanation = `${item.name} is ${
          item.performance >= 0 ? "up" : "down"
        } ${Math.abs(item.performance).toFixed(2)}% likely due to ${sentimentText} news from ${
          mostRelevantNews.source
        }: "${mostRelevantNews.summary || mostRelevantNews.title}"`;
        
        // Add extra context if it's a mutual fund or ETF
        if (item.type === "MutualFund" || item.type === "ETF") {
          explanation += `. This ${item.type.toLowerCase()} is primarily invested in the ${item.sector} sector, which has been ${
            item.performance >= 0 ? "performing well" : "under pressure"
          } recently.`;
        } else {
          // For stocks
          explanation += `. As a ${item.sector} sector company, ${item.name}'s performance is affected by overall sector trends.`;
        }
      }
    }
  }

  return explanation;
};

/**
 * Generates a detailed analysis of a financial instrument based on news, price movements,
 * and sentiment analysis
 * 
 * @param query The user's search query
 * @param item The financial item to analyze
 * @param relatedNews News items related to the financial item
 * @returns A detailed analysis as a formatted string
 */
export const generateDetailedAnalysis = async (
  query: string,
  item: FinancialItem,
  relatedNews: NewsItem[]
): Promise<string> => {
  // Simulate processing delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Get basic explanation first
  const basicExplanation = await generateExplanation(query, item, relatedNews);
  
  // Initialize the detailed analysis with the instrument info
  let analysis = `📊 Analysis for ${item.name} (${item.type})\n`;
  analysis += `────────────────────────\n`;
  analysis += `Current performance: ${item.performance >= 0 ? "▲" : "▼"} ${Math.abs(item.performance).toFixed(2)}%\n`;
  analysis += `Sector: ${item.sector}\n`;
  analysis += `────────────────────────\n\n`;

  // Add price movement analysis
  analysis += `💹 Price Movement Analysis:\n`;
  if (Math.abs(item.performance) > 5) {
    analysis += `This is a significant ${item.performance >= 0 ? "increase" : "decrease"} that likely reflects important market events.\n`;
  } else if (Math.abs(item.performance) > 2) {
    analysis += `This ${item.performance >= 0 ? "gain" : "loss"} is moderate and may be influenced by sector-wide trends.\n`;
  } else {
    analysis += `This is a relatively small change, potentially just normal market fluctuation.\n`;
  }

  analysis += `Compared to the overall market, this performance is ${compareToMarket(item.performance, item.changePercent)}.\n\n`;

  // Add news sentiment analysis if we have related news
  if (relatedNews?.length > 0) {
    const sentimentCounts = {
      positive: 0,
      negative: 0,
      neutral: 0,
      mixed: 0
    };
    
    relatedNews.forEach(news => {
      sentimentCounts[news.sentiment]++;
    });
    
    const totalNews = relatedNews.length;
    const sentimentDistribution = Object.entries(sentimentCounts)
      .map(([sentiment, count]) => ({
        sentiment,
        percentage: Math.round((count / totalNews) * 100)
      }))
      .filter(item => item.percentage > 0)
      .sort((a, b) => b.percentage - a.percentage);
      
    analysis += `📰 News Sentiment Analysis:\n`;
    analysis += `Based on ${totalNews} related news articles:\n`;
    
    sentimentDistribution.forEach(({ sentiment, percentage }) => {
      const emoji = sentiment === 'positive' ? '✅' : sentiment === 'negative' ? '❌' : sentiment === 'neutral' ? '⚪' : '🔄';
      analysis += `${emoji} ${percentage}% ${sentiment}\n`;
    });
    
    // Get the dominant sentiment
    const dominantSentiment = sentimentDistribution[0]?.sentiment || 'neutral';
    
    // Add interpretation
    analysis += `\nThe dominant sentiment is ${dominantSentiment}, which ${
      dominantSentiment === 'positive' ? 'supports upward price movement' : 
      dominantSentiment === 'negative' ? 'puts downward pressure on the price' : 
      'suggests market uncertainty'
    }.\n\n`;

    // Top news mentions
    analysis += `📊 Top News Mentions:\n`;
    const topNews = [...relatedNews]
      .sort((a, b) => {
        // Sort by impact first
        const impactOrder = { high: 3, medium: 2, low: 1 };
        const impactDiff = (impactOrder[b.impact] || 0) - (impactOrder[a.impact] || 0);
        
        if (impactDiff !== 0) return impactDiff;
        
        // Then by date
        return new Date(b.date).getTime() - new Date(a.date).getTime();
      })
      .slice(0, 3);
      
    topNews.forEach((news, index) => {
      const sentimentEmoji = 
        news.sentiment === 'positive' ? '✅' : 
        news.sentiment === 'negative' ? '❌' : 
        news.sentiment === 'neutral' ? '⚪' : '🔄';
        
      analysis += `${index + 1}. ${sentimentEmoji} "${news.title}" (${news.source}) - ${formatDate(news.date)}\n`;
    });
    
    analysis += `\n`;
  } else {
    analysis += `📰 No recent news articles found specifically mentioning this instrument.\n\n`;
  }
  
  // Add insights based on the financial instrument type
  analysis += `🔍 Key Insights:\n`;
  if (item.type === "MutualFund" || item.type === "ETF") {
    analysis += `• This ${item.type.toLowerCase()} is focused on the ${item.sector} sector\n`;
    if (item.holdings && item.holdings.length > 0) {
      // Add top holdings if available
      analysis += `• Top holdings include: ${item.holdings.slice(0, 3).map(h => h.stockName).join(", ")}\n`;
      
      // Add weighted performance insights if relevant
      const topHoldingName = item.holdings[0]?.stockName;
      if (topHoldingName) {
        analysis += `• Performance is likely influenced by its top holding: ${topHoldingName}\n`;
      }
    }
  } else if (item.type === "Stock") {
    // For stocks
    analysis += `• As a ${item.sector} sector company, it is affected by industry-specific trends\n`;
    analysis += `• Recent price ${item.performance >= 0 ? "gains" : "losses"} should be evaluated against sector peers\n`;
    analysis += `• Technical indicators suggest ${getTechnicalIndication(item.performance, item.changePercent)}\n`;
  }
  
  // Final summary and forecast
  analysis += `\n📈 Summary:\n`;
  analysis += basicExplanation;
  analysis += `\n\nBased on the analysis, the near-term outlook appears ${getPriceOutlook(item, relatedNews)}.`;

  return analysis;
};

/**
 * Compare instrument performance to overall market
 */
const compareToMarket = (performance: number, marketChange: number): string => {
  const difference = performance - marketChange;
  
  if (Math.abs(difference) < 0.5) {
    return "in line with the broader market";
  } else if (difference > 0) {
    return `outperforming the broader market by ${difference.toFixed(2)}%`;
  } else {
    return `underperforming the broader market by ${Math.abs(difference).toFixed(2)}%`;
  }
};

/**
 * Get a technical analysis indication based on performance metrics
 */
const getTechnicalIndication = (performance: number, changePercent: number): string => {
  if (performance > 5 && changePercent > 0) {
    return "possible overbought conditions";
  } else if (performance < -5 && changePercent < 0) {
    return "possible oversold conditions";
  } else if (performance > 0 && changePercent > 0) {
    return "continued upward momentum";
  } else if (performance < 0 && changePercent < 0) {
    return "continued downward pressure";
  } else if (performance > 0 && changePercent < 0) {
    return "potential reversal of upward trend";
  } else if (performance < 0 && changePercent > 0) {
    return "potential recovery from recent lows";
  }
  return "mixed signals";
};

/**
 * Get price outlook based on financial item and news
 */
const getPriceOutlook = (item: FinancialItem, news: NewsItem[]): string => {
  // Count positive and negative news
  let positiveCount = 0;
  let negativeCount = 0;
  
  news.forEach(article => {
    if (article.sentiment === 'positive') positiveCount++;
    if (article.sentiment === 'negative') negativeCount++;
  });
  
  // Determine news sentiment balance
  const newsSentiment = positiveCount > negativeCount ? 'positive' : 
                        negativeCount > positiveCount ? 'negative' : 'neutral';
  
  // Performance direction
  const performanceDirection = item.performance >= 0 ? 'positive' : 'negative';
  
  // If news sentiment aligns with performance direction, it reinforces the trend
  if (newsSentiment === performanceDirection) {
    return performanceDirection === 'positive' ? 'bullish' : 'bearish';
  } else if (newsSentiment === 'neutral') {
    return 'cautiously ' + (performanceDirection === 'positive' ? 'optimistic' : 'pessimistic');
  } else {
    // News sentiment contradicts performance, suggesting potential reversal
    return 'mixed, with potential for trend reversal';
  }
};

/**
 * Format a date string to a more readable format
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric'
  });
};

/**
 * Extracts keywords from text content
 * 
 * @param text The text to extract keywords from
 * @returns An array of important keywords
 */
export const extractKeywords = (text: string): string[] => {
  // A simple implementation that just splits the text and removes common words
  // In a real application, this would use more sophisticated NLP techniques
  const stopwords = ["a", "an", "the", "in", "on", "at", "to", "for", "with", "by", "of", "is", "are", "was", "were"];
  
  return text
    .toLowerCase()
    .replace(/[^\w\s]/g, '')
    .split(/\s+/)
    .filter(word => word.length > 2 && !stopwords.includes(word))
    .slice(0, 10);
};

/**
 * Analyzes the sentiment of a text
 * 
 * @param text The text to analyze
 * @returns A sentiment value (positive, negative, neutral, or mixed)
 */
export const analyzeSentiment = (text: string): "positive" | "negative" | "neutral" | "mixed" => {
  // A very simplified sentiment analysis
  // In a real application, this would use a proper NLP model
  const positiveWords = ["up", "rise", "gain", "growth", "profit", "positive", "increase", "improve", "success"];
  const negativeWords = ["down", "fall", "loss", "decline", "negative", "decrease", "drop", "concern", "risk", "fear"];
  
  let positiveCount = 0;
  let negativeCount = 0;
  
  const words = text.toLowerCase().split(/\s+/);
  
  for (const word of words) {
    if (positiveWords.some(pw => word.includes(pw))) {
      positiveCount++;
    }
    if (negativeWords.some(nw => word.includes(nw))) {
      negativeCount++;
    }
  }
  
  if (positiveCount > negativeCount * 2) {
    return "positive";
  } else if (negativeCount > positiveCount * 2) {
    return "negative";
  } else if (positiveCount === 0 && negativeCount === 0) {
    return "neutral";
  } else {
    return "mixed";
  }
};
