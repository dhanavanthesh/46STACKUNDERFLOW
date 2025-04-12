
export interface FinancialItem {
  id: string;
  name: string;
  type: "MutualFund" | "Stock" | "ETF";
  isin?: string;
  ticker?: string;
  sector: string;
  performance: number;
  changePercent: number;
  price?: number;
  nav?: number;
  holdings?: Array<{
    stockId: string;
    stockName: string;
    weight: number;
  }>;
}

export interface NewsItem {
  id: string;
  title: string;
  date: string;
  source: string;
  url: string;
  content: string;
  summary: string;
  sentiment: "positive" | "negative" | "neutral" | "mixed";
  impact: "high" | "medium" | "low";
  entities: string[];
  keywords: string[];
  relatedSecurities?: string[];
}

export interface SearchQuery {
  query: string;
  type?: "MutualFund" | "Stock" | "ETF" | "All";
  timeRange?: "day" | "week" | "month" | "year" | "all";
}
