
import { NewsItem } from "@/types";

// Simulate news API - in a real app this would fetch from a scraper or API
export const fetchLatestNews = async (category?: string): Promise<NewsItem[]> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  const allNews: NewsItem[] = [
    {
      id: "n001",
      title: "RBI Keeps Repo Rate Unchanged at 6.5%, Nifty Reacts Positively",
      date: "2025-04-10T10:30:00Z",
      source: "The Hindu",
      url: "https://www.thehindu.com/business/Economy/rbi-monetary-policy-committee-repo-rate-unchanged-shaktikanta-das-december-6-2024/article68953744.ece",
      content: "The Reserve Bank of India (RBI) maintained the repo rate at 6.5% for the seventh consecutive policy meeting, in line with expectations. The central bank cited concerns about inflation while maintaining its growth projections at 7% for the fiscal year. Markets reacted positively to the policy continuity.",
      summary: "RBI maintains status quo on repo rate at 6.5%, keeping its stance unchanged while citing inflation concerns.",
      sentiment: "positive",
      impact: "high",
      entities: ["RBI", "Nifty", "Repo Rate"],
      keywords: ["monetary policy", "interest rates", "inflation"]
    },
    {
      id: "n002",
      title: "HDFC Bank Reports 15% Rise in Q4 Net Profit",
      date: "2025-04-09T14:45:00Z",
      source: "Financial Express",
      url: "https://www.financialexpress.com/market/hdfc-bank-q4-net-profit-jumps-15-on-year-to-rs-7280-cr-provisions-double-to-rs-3785-cr-1932544/",
      content: "HDFC Bank reported a 15% year-on-year increase in net profit for Q4 FY25, reaching ₹12,580 crore, slightly above analyst estimates. The bank's net interest income grew by 12%, while its gross non-performing assets (NPAs) remained stable at 1.3%. The board has recommended a dividend of ₹19 per share.",
      summary: "HDFC Bank's Q4 profits exceeded expectations with 15% YoY growth and steady asset quality.",
      sentiment: "positive",
      impact: "medium",
      entities: ["HDFC Bank", "Banking Sector"],
      keywords: ["Q4 results", "profit", "dividend", "banking"]
    },
    {
      id: "n003",
      title: "Tech Stocks Tumble as US Inflation Data Disappoints",
      date: "2025-04-08T16:20:00Z",
      source: "Economic Times",
      url: "https://economictimes.indiatimes.com/markets/stocks/news/wall-street-stocks-end-lower-after-inflation-data-tech-stocks-push-nasdaq-down/articleshow/115750468.cms",
      content: "Indian technology stocks faced significant selling pressure following disappointing inflation data from the US, which raised concerns about potential aggressive rate hikes by the Federal Reserve. Major IT companies like Infosys, TCS, and HCL Technologies dropped between 2-4%, dragging the Nifty IT index down by 3.2%.",
      summary: "Tech stocks declined after US inflation data raised fears of aggressive Fed rate hikes.",
      sentiment: "negative",
      impact: "high",
      entities: ["Infosys", "TCS", "HCL Technologies", "Nifty IT"],
      keywords: ["tech stocks", "US inflation", "Federal Reserve", "rate hikes"]
    },
    {
      id: "n004",
      title: "Jyothy Labs Surges 8% on Strong Sales Outlook",
      date: "2025-04-11T09:15:00Z",
      source: "CNBC TV18",
      url: "https://www.cnbctv18.com/market/jyothy-labs-share-price-q3-results-reports-volume-growth-8-pc-despite-headwinds-margin-contracts-19549842.htm",
      content: "Shares of Jyothy Labs surged over 8% in today's trading session after the company provided a strong sales outlook for FY26. Management expects double-digit volume growth driven by rural recovery and new product launches in the home care and personal care segments. Several brokerages have upgraded the stock following the announcement.",
      summary: "Jyothy Labs stock jumped 8% after announcing strong sales outlook and rural market recovery.",
      sentiment: "positive",
      impact: "medium",
      entities: ["Jyothy Labs", "FMCG Sector"],
      keywords: ["FMCG", "rural recovery", "volume growth", "outlook"]
    },
    {
      id: "n005",
      title: "Global Economic Concerns Weigh on Nifty, Closes 0.5% Lower",
      date: "2025-04-10T15:45:00Z",
      source: "The Hindu Business Line",
      url: "https://www.thehindubusinessline.com/markets/stock-markets/sensex-nifty-open-lower-amid-global-economic-concerns/article68620735.ece#:~:text=The%20benchmark%20Sensex%20fell%20210.18%20points%20to%20open,jobs%20data%2C%20which%20reignited%20fears%20of%20a%20recession.",
      content: "The Nifty index closed 0.5% lower today, ending a three-day winning streak, as concerns about global economic slowdown weighed on investor sentiment. Banking and metal sectors were the biggest losers, while pharma stocks showed some resilience. Foreign portfolio investors (FPIs) were net sellers in Indian equities, pulling out over ₹1,200 crore.",
      summary: "Nifty ended 0.5% lower due to global economic concerns, with banking and metal sectors leading the decline.",
      sentiment: "negative",
      impact: "medium",
      entities: ["Nifty", "Banking Sector", "Metal Sector", "Pharma Sector"],
      keywords: ["market decline", "global economy", "FPI outflow", "sector performance"]
    },
    {
      id: "n006",
      title: "SBI Mutual Fund Launches New Small Cap Fund, Aims to Raise ₹2,000 Crore",
      date: "2025-04-07T11:30:00Z",
      source: "Economic Times",
      url: "https://economictimes.indiatimes.com/mf/mf-news/sbi-mutual-fund-launches-small-cap-mid-cap-equity-index-funds/articleshow/94342876.cms",
      content: "SBI Mutual Fund has launched a new small cap fund aiming to raise ₹2,000 crore during its New Fund Offer (NFO) period. The fund will focus on companies with market capitalization below ₹10,000 crore and will be managed by veteran fund manager Saurabh Jain. The NFO opens on April 15 and will close on April 29.",
      summary: "SBI Mutual Fund launches new small cap fund with ₹2,000 crore target, NFO opening on April 15.",
      sentiment: "positive",
      impact: "medium",
      entities: ["SBI Mutual Fund", "Small Cap", "SBI Blue Chip Fund"],
      keywords: ["mutual fund", "NFO", "small cap", "investment"]
    },
    {
      id: "n007",
      title: "Pharmaceutical Sector Shines Amid Market Volatility, Nippon Pharma Fund Up 4%",
      date: "2025-04-09T13:10:00Z",
      source: "Moneycontrol",
      url: "https://www.moneycontrol.com/news/business/markets/pharma-healthcare-stocks-rise-as-defensive-plays-shine-amid-market-volatility-12816136.html",
      content: "The pharmaceutical sector has emerged as a defensive bet amid recent market volatility, with the Nifty Pharma index gaining 3.5% this week while the broader market remained flat. Funds focused on the sector, including Nippon India Pharma Fund, have delivered strong returns of around 4% over the past week, attracting investor interest.",
      summary: "Pharma sector showed strong performance during market volatility, with Nippon Pharma Fund gaining 4%.",
      sentiment: "positive",
      impact: "medium",
      entities: ["Pharmaceutical Sector", "Nifty Pharma", "Nippon India Pharma Fund"],
      keywords: ["pharma stocks", "defensive sector", "fund performance", "volatility"]
    },
    {
      id: "n008",
      title: "PM Modi's Semicon India 2024 speech fuels rally in semiconductor stocks",
      date: "2025-04-08T10:45:00Z",
      source: "Moneycontrol",
      url: "https://www.moneycontrol.com/news/business/markets/pm-modis-semicon-india-2024-speech-fuels-rally-in-semiconductor-stocks-12819379.html",
      content: "The Indian government announced a new semiconductor policy with incentives worth ₹76,000 crore to boost domestic manufacturing and attract global players. The policy aims to establish India as a global hub for electronics system design and manufacturing. Technology and electronics stocks rallied on the news, with the sector gaining over 2%.",
      summary: "Tech stocks rallied after government announced new semiconductor policy with ₹76,000 crore incentives.",
      sentiment: "positive",
      impact: "high",
      entities: ["Technology Sector", "Government Policy", "ICICI Prudential Technology Fund"],
      keywords: ["semiconductor", "manufacturing", "policy", "incentives"]
    },
    {
      id: "n009",
      title: "Gold Prices Hit Record High Amid Global Uncertainty",
      date: "2025-04-12T09:30:00Z",
      source: "Business Today",
      url: "https://www.businesstoday.in/personal-finance/investment/story/gold-prices-reach-all-time-highs-amid-economic-uncertainty-471736-2025-04-11",
      content: "Gold prices surged to a record high of ₹62,500 per 10 grams in the domestic market, tracking global trends as investors sought safe-haven assets amid economic uncertainty. The rally was supported by a weaker rupee and expectations of a pause in US rate hikes. Analysts expect the uptrend to continue in the near term.",
      summary: "Gold prices hit record high as investors flock to safe-haven assets amid economic uncertainty.",
      sentiment: "positive",
      impact: "medium",
      entities: ["Gold", "Rupee", "US Federal Reserve"],
      keywords: ["gold prices", "safe haven", "economic uncertainty", "rate hikes"]
    },
    {
      id: "n010",
      title: "Adani Ports Secures Major Contract for New Container Terminal",
      date: "2025-04-11T11:20:00Z",
      source: "India Today",
      url: "https://www.indiatoday.in/india/story/adani-ports-syama-prasad-mookerjee-port-kolkata-deal-apsez-2550703-2024-06-08",
      content: "Adani Ports and Special Economic Zone (APSEZ) has secured a ₹7,200 crore contract to develop a new container terminal at Jawaharlal Nehru Port Trust (JNPT). The project, expected to be completed by 2027, will significantly boost the port's capacity and is seen as a major win for India's infrastructure sector.",
      summary: "Adani Ports wins ₹7,200 crore contract to develop new container terminal at JNPT.",
      sentiment: "positive",
      impact: "high",
      entities: ["Adani Ports", "JNPT", "Infrastructure Sector"],
      keywords: ["ports", "infrastructure", "contract", "logistics"]
    },
    {
      id: "n011",
      title: "Auto Sales Decline for Third Consecutive Month",
      date: "2025-04-10T14:15:00Z",
      source: "HDFC ERGO",
      url: "https://www.hdfcergo.com/news/car-insurance/car-sales-slow-down-for-third-consecutive-month-in-june-2024",
      content: "Domestic passenger vehicle sales declined by 8% in March, marking the third consecutive month of contraction, as high interest rates and inflationary pressures continued to dampen demand. Market leaders Maruti Suzuki and Hyundai reported sales drops of 9% and 7% respectively, while Tata Motors bucked the trend with 3% growth.",
      summary: "Auto sales decline for third straight month due to high interest rates and inflation.",
      sentiment: "negative",
      impact: "medium",
      entities: ["Maruti Suzuki", "Hyundai", "Tata Motors", "Auto Sector"],
      keywords: ["auto sales", "interest rates", "inflation", "demand"]
    },
    {
      id: "n012",
      title: "Zomato Reports First Profitable Quarter Since IPO",
      date: "2025-04-09T16:40:00Z",
      source: "Business Today",
      url: "https://www.bing.com/search?pglt=931&q=Zomato+Reports+First+Profitable+Quarter+Since+IPO&cvid=4a12077005aa477a808b09f90de6daf5&gs_lcrp=EgRlZGdlKgYIABBFGDkyBggAEEUYOdIBBzE3M2owajGoAgCwAgA&FORM=ANNTA1&ucpdpc=UCPD&PC=HCTS",
      content: "Food delivery platform Zomato reported its first profitable quarter since going public, with net profit of ₹120 crore in Q4 FY25, compared to a loss of ₹360 crore in the same period last year. The company attributed the turnaround to cost optimization and growth in its quick commerce business. Shares surged 12% post-announcement.",
      summary: "Zomato reports first profitable quarter since IPO, shares jump 12%.",
      sentiment: "positive",
      impact: "high",
      entities: ["Zomato", "Food Delivery", "Quick Commerce"],
      keywords: ["profitability", "food tech", "earnings", "turnaround"]
    },
    {
      id: "n013",
      title: "Oil Prices Spike 5% After Middle East Tensions Escalate",
      date: "2025-04-08T12:10:00Z",
      source: "Times of India",
      url: "https://timesofindia.indiatimes.com/business/international-business/oil-prices-surge-over-5-amid-escalating-conflict-in-middle-east/articleshow/113916061.cms",
      content: "Global oil prices jumped 5% to $92 per barrel after fresh tensions in the Middle East raised concerns about supply disruptions. The rally impacted Indian oil marketing companies, with HPCL, BPCL and IOCL shares falling 2-3% on fears of margin pressure. Analysts warn of potential fuel price hikes if the situation worsens.",
      summary: "Oil prices surge 5% on Middle East tensions, raising concerns about fuel prices.",
      sentiment: "negative",
      impact: "high",
      entities: ["Crude Oil", "HPCL", "BPCL", "IOCL"],
      keywords: ["oil prices", "Middle East", "supply disruption", "fuel prices"]
    },
    {
      id: "n014",
      title: "Paytm Payments Bank Gets RBI Nod to Resume Onboarding New Customers",
      date: "2025-04-07T10:25:00Z",
      source: "Good Returns",
      url: "https://www.goodreturns.in/news/paytm-gets-npci-nod-to-resume-onboarding-new-upi-users-after-rbi-sanctions-in-march-explained-1383945.html",
      content: "The Reserve Bank of India has allowed Paytm Payments Bank to resume onboarding new customers after nearly a year-long ban, subject to certain conditions. The approval comes after the bank addressed compliance issues related to IT systems and data security. Paytm shares rose 8% on the news.",
      summary: "Paytm Payments Bank gets RBI approval to restart customer onboarding after compliance fixes.",
      sentiment: "positive",
      impact: "medium",
      entities: ["Paytm", "RBI", "Payments Bank"],
      keywords: ["banking", "regulatory approval", "compliance", "fintech"]
    },
    {
      id: "n015",
      title: "Indian Railways Plans ₹2.4 Lakh Crore Capex for FY26",
      date: "2025-04-06T15:30:00Z",
      source: "Upstox",
      url: "https://upstox.com/news/market-news/latest-updates/budget-2025-a-look-at-railway-ministry-capex-utilisation-amid-expectations-of-higher-allocation/article-142232/",
      content: "Indian Railways has proposed a record capital expenditure of ₹2.4 lakh crore for FY26, focusing on track expansion, electrification and station redevelopment. The plan includes 4,500 km of new lines and 5,000 km of electrification. Railway stocks like IRCTC, Titagarh Wagons and Texmaco surged 3-5% on the announcement.",
      summary: "Indian Railways proposes ₹2.4 lakh crore capex for FY26, focusing on infrastructure expansion.",
      sentiment: "positive",
      impact: "high",
      entities: ["Indian Railways", "IRCTC", "Titagarh Wagons", "Texmaco"],
      keywords: ["infrastructure", "capex", "railways", "investment"]
    },
    {
      id: "n016",
      title: "Byju's Faces Investor Lawsuit Over $1.2 Billion Loan Dispute",
      date: "2025-04-05T13:50:00Z",
      source: "India Today",
      url: "https://www.indiatoday.in/business/story/byjus-faces-setback-us-court-delaware-upholds-usd-12-billion-loan-default-ruling-glas-trust-llc-2605485-2024-09-24",
      content: "Edtech giant Byju's is facing a lawsuit from a group of investors over a $1.2 billion term loan, with allegations of fund diversion and financial mismanagement. The legal battle comes as the company struggles with valuation markdowns and layoffs. The news sent shockwaves through India's startup ecosystem.",
      summary: "Byju's faces investor lawsuit over $1.2 billion loan dispute amid financial troubles.",
      sentiment: "negative",
      impact: "high",
      entities: ["Byju's", "Edtech", "Startup Ecosystem"],
      keywords: ["lawsuit", "funding", "financial trouble", "edtech"]
    }
  ];
  
  if (category && category !== "all") {
    // Filter by category (simplified mapping)
    const categoryToEntities: Record<string, string[]> = {
      "markets": ["Nifty", "Banking Sector", "Metal Sector"],
      "economy": ["RBI", "Government Policy"],
      "companies": ["HDFC Bank", "Jyothy Labs", "Reliance Industries", "Infosys"]
    };
    
    return allNews.filter(news => 
      news.entities.some(entity => categoryToEntities[category]?.includes(entity))
    );
  }
  
  return allNews;
};

export const fetchNewsForQuery = async (query: string): Promise<NewsItem[]> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // In a real app, this would call an API with the search query
  const allNews = await fetchLatestNews();
  
  // Basic search logic - in a real app this would be more sophisticated
  const queryTerms = query.toLowerCase().split(" ");
  
  return allNews.filter(news => {
    const newsText = `${news.title} ${news.content} ${news.entities.join(" ")}`.toLowerCase();
    return queryTerms.some(term => newsText.includes(term));
  });
};
