
import { NewsItem } from "@/types";
import { analyzeSentiment, extractKeywords } from "./nlpUtils";

/**
 * Fetch real-time news from various sources related to a specific financial instrument
 * 
 * @param query The search query or financial instrument name
 * @returns Array of news items related to the query
 */
export const fetchRealtimeNews = async (query: string): Promise<NewsItem[]> => {
  // In a production environment, this would use real web scraping
  // For this demo, we'll simulate fetching news with a delay and mock data
  console.log(`[Scraper] Fetching news for: ${query}`);
  
  // Add random delay to simulate real scraping (300-1200ms)
  const delay = 300 + Math.random() * 900;
  await new Promise(resolve => setTimeout(resolve, delay));
  
  // Generate some mock news based on the query
  const mockNews = generateMockNews(query);
  
  // Process the mock news to simulate scraping and analysis
  const processedNews = mockNews.map(news => {
    // Extract entities (mentions of companies, sectors, etc.)
    const entities = [...extractEntitiesFromTitle(news.title), query];
    
    // Extract keywords
    const keywords = extractKeywords(news.content);
    
    // Analyze sentiment
    const sentiment = analyzeSentiment(news.content);
    
    // Determine impact based on content length and sentiment
    const impact = determineImpact(news.content, sentiment);
    
    return {
      ...news,
      entities: [...new Set(entities)], // Remove duplicates
      keywords,
      sentiment,
      impact
    };
  });
  
  console.log(`[Scraper] Found ${processedNews.length} news items for: ${query}`);
  return processedNews;
};

/**
 * Extract entities (company names, etc.) from news title
 */
const extractEntitiesFromTitle = (title: string): string[] => {
  const entities: string[] = [];
  
  // This is a simplified version. In a real application, 
  // we would use named entity recognition (NER) models
  const potentialEntities = [
    "Nifty", "Sensex", "RBI", "SEBI", "BSE", "NSE",
    "HDFC", "ICICI", "SBI", "Axis", "Reliance", "Infosys", "TCS", 
    "Adani", "Tata", "Bajaj", "Kotak", "Jyothy Labs",
    "Banking Sector", "IT Sector", "Pharma Sector", "FMCG Sector"
  ];
  
  for (const entity of potentialEntities) {
    if (title.includes(entity)) {
      entities.push(entity);
    }
  }
  
  return entities;
};

/**
 * Determine the impact level of a news article
 */
const determineImpact = (content: string, sentiment: string): "high" | "medium" | "low" => {
  const contentLength = content.length;
  
  // More detailed news tends to have higher impact
  if (contentLength > 500 && (sentiment === "positive" || sentiment === "negative")) {
    return "high";
  } else if (contentLength > 300 || sentiment !== "neutral") {
    return "medium";
  } else {
    return "low";
  }
};

/**
 * Generate mock news for demonstration purposes
 */
const generateMockNews = (query: string): NewsItem[] => {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  
  const twoDaysAgo = new Date(today);
  twoDaysAgo.setDate(today.getDate() - 2);
  
  const threeDaysAgo = new Date(today);
  threeDaysAgo.setDate(today.getDate() - 3);
  
  // Base mock news templates
  const newsTemplates: Partial<NewsItem>[] = [
    {
      title: `${query} reports strong quarterly results, exceeding analyst expectations`,
      content: `${query} announced its quarterly results today, with profits up 15% year-over-year, significantly exceeding analyst expectations of 8% growth. The company attributed this performance to strong demand in emerging markets and effective cost management strategies. CEO mentioned that they expect this momentum to continue into the next quarter.`,
      source: "Financial Express",
      date: today.toISOString(),
      url: "https://financialexpress.com/markets/quarterly-results",
      summary: `${query} exceeded profit expectations with 15% YoY growth due to strong demand in emerging markets.`
    },
    {
      title: `Market analysts upgrade ${query} rating to "Buy"`,
      content: `Several leading market analysts have upgraded their rating for ${query} from "Hold" to "Buy" following recent positive developments in the sector. The consensus target price has been raised by 12%, reflecting increased confidence in the company's growth strategy and market position. Trading volume has increased significantly since the announcement.`,
      source: "Economic Times",
      date: yesterday.toISOString(),
      url: "https://economictimes.com/markets/analyst-ratings",
      summary: `Analysts upgraded ${query} to "Buy" with a 12% higher target price based on strong growth outlook.`
    },
    {
      title: `${query} faces regulatory scrutiny over compliance issues`,
      content: `Regulatory authorities have launched an investigation into ${query}'s compliance practices following reports of potential irregularities in its financial reporting. The company has stated that it is fully cooperating with authorities but maintains that all its practices are in accordance with relevant regulations. The stock dropped 3% following the news.`,
      source: "Business Standard",
      date: yesterday.toISOString(),
      url: "https://business-standard.com/markets/regulatory-news",
      summary: `${query} under regulatory investigation for potential financial reporting irregularities.`
    },
    {
      title: `${query} announces expansion into new markets`,
      content: `${query} has announced plans to expand operations into three new international markets over the next fiscal year. The expansion represents a significant step in the company's global growth strategy and is expected to contribute an additional 8-10% to annual revenue once fully operational. The company will be investing approximately ₹500 crore in this initiative.`,
      source: "LiveMint",
      date: twoDaysAgo.toISOString(),
      url: "https://livemint.com/companies/expansion-news",
      summary: `${query} plans expansion into three new international markets with ₹500 crore investment.`
    },
    {
      title: `${query} sees neutral trading amid broader market volatility`,
      content: `Shares of ${query} traded relatively flat today, showing resilience amid broader market volatility. While most sector peers experienced significant fluctuations, ${query} maintained stable price levels, which analysts attribute to its strong fundamentals and balanced risk profile. Trading volumes were in line with the 30-day average.`,
      source: "Moneycontrol",
      date: today.toISOString(),
      url: "https://moneycontrol.com/markets/daily-trading",
      summary: `${query} remained stable amid market volatility, showing resilience compared to sector peers.`
    },
    {
      title: `${query} announces leadership change, CFO to step down`,
      content: `${query} announced today that its Chief Financial Officer will be stepping down after 5 years in the role. The company has initiated a search for a successor and expects a smooth transition over the next quarter. The departing CFO cited personal reasons for the decision. The news has created some uncertainty among investors.`,
      source: "CNBC-TV18",
      date: threeDaysAgo.toISOString(),
      url: "https://cnbctv18.com/market/corporate-news",
      summary: `${query}'s CFO to step down after 5 years, company initiates search for successor.`
    }
  ];
  
  // Randomly select 3-5 news items
  const numberOfNews = 3 + Math.floor(Math.random() * 3);
  const shuffledNews = [...newsTemplates].sort(() => 0.5 - Math.random());
  const selectedNews = shuffledNews.slice(0, numberOfNews);
  
  // Add unique IDs and complete the news items
  return selectedNews.map((news, index) => ({
    id: `mock-${query.replace(/\s+/g, '-').toLowerCase()}-${index}`,
    title: news.title || `News about ${query}`,
    date: news.date || new Date().toISOString(),
    source: news.source || "Financial News",
    url: news.url || "https://example.com/financial-news",
    content: news.content || `This is a news article about ${query}.`,
    summary: news.summary || `News summary about ${query}`,
    sentiment: "neutral" as "positive" | "negative" | "neutral" | "mixed", // Fix: Use type assertion to specify literal type
    impact: "medium" as "high" | "medium" | "low", // Fix: Use type assertion for impact too
    entities: [query], // Will be extracted later
    keywords: [], // Will be extracted later
  }));
};

/**
 * Scrapes specific financial news sources for recent articles
 * This would be implemented with real scraping in a production environment
 */
export const scrapeFinancialNewsSites = async (): Promise<NewsItem[]> => {
  // In a real implementation, this would use libraries like Puppeteer, Playwright, or Cheerio
  // to scrape actual financial news websites
  console.log('[Scraper] Scraping financial news sites for recent articles');
  
  // Simulate scraping delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  // Return some mock general financial news
  const mockGeneralNews: NewsItem[] = [
    {
      id: "general-001",
      title: "RBI Maintains Status Quo on Repo Rate at 6.5%",
      date: new Date().toISOString(),
      source: "Economic Times",
      url: "https://economictimes.com/markets/rbi-repo-rate",
      content: "The Reserve Bank of India (RBI) maintained the repo rate at 6.5% for the eighth consecutive policy meeting, in line with market expectations. The central bank cited inflation concerns while maintaining its growth forecast at 7.2% for the current fiscal year. Governor Shaktikanta Das emphasized the need for continued vigilance against inflationary pressures.",
      summary: "RBI keeps repo rate unchanged at 6.5%, maintains growth outlook at 7.2%.",
      sentiment: "neutral",
      impact: "high",
      entities: ["RBI", "Repo Rate"],
      keywords: ["repo rate", "monetary policy", "inflation", "rbi"]
    },
    {
      id: "general-002",
      title: "IT Sector Leads Market Rally on Strong US Tech Earnings",
      date: new Date().toISOString(),
      source: "Moneycontrol",
      url: "https://moneycontrol.com/markets/it-sector-rally",
      content: "The IT sector led the market rally today following strong earnings reports from major US technology companies. Indian IT firms, which derive a significant portion of their revenue from US clients, saw their stocks rise by 2-4% on average. Analysts suggest this indicates a potential increase in technology spending by US corporations in the coming quarters.",
      summary: "IT sector stocks rally 2-4% following positive US tech earnings reports.",
      sentiment: "positive",
      impact: "medium",
      entities: ["IT Sector", "Technology Sector"],
      keywords: ["IT", "rally", "tech stocks", "earnings"]
    }
  ];
  
  return mockGeneralNews;
};
