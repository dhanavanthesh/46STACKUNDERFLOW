
import { FinancialItem } from "@/types";

// Simulated data - in a real app, this would come from an API or JSON files
export const fetchMutualFundsData = async (): Promise<FinancialItem[]> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Mock data for mutual funds
  return [
    {
      id: "mf001",
      name: "SBI Blue Chip Fund",
      type: "MutualFund",
      isin: "INF123D01AB2",
      sector: "Large Cap",
      performance: 3.25,
      changePercent: 0.45,
      nav: 58.75,
      holdings: [
        { stockId: "s001", stockName: "Reliance Industries", weight: 8.2 },
        { stockId: "s002", stockName: "HDFC Bank", weight: 7.5 },
        { stockId: "s003", stockName: "Infosys", weight: 6.3 },
      ]
    },
    {
      id: "mf002",
      name: "HDFC Mid-Cap Opportunities",
      type: "MutualFund",
      isin: "INF123D02CD3",
      sector: "Mid Cap",
      performance: -1.78,
      changePercent: -0.32,
      nav: 82.15,
      holdings: [
        { stockId: "s005", stockName: "Bajaj Finance", weight: 5.8 },
        { stockId: "s006", stockName: "Titan Company", weight: 4.9 },
        { stockId: "s007", stockName: "Tata Motors", weight: 4.2 },
      ]
    },
    {
      id: "mf003",
      name: "Axis Small Cap Fund",
      type: "MutualFund",
      isin: "INF123D03EF4",
      sector: "Small Cap",
      performance: 5.42,
      changePercent: 0.89,
      nav: 44.60,
      holdings: [
        { stockId: "s008", stockName: "IndiaMART", weight: 3.9 },
        { stockId: "s009", stockName: "KPIT Technologies", weight: 3.7 },
        { stockId: "s010", stockName: "Mastek", weight: 3.5 },
      ]
    },
    {
      id: "mf004",
      name: "ICICI Prudential Technology Fund",
      type: "MutualFund",
      isin: "INF123D04GH5",
      sector: "Technology",
      performance: -2.15,
      changePercent: -0.53,
      nav: 120.30,
      holdings: [
        { stockId: "s003", stockName: "Infosys", weight: 9.2 },
        { stockId: "s011", stockName: "TCS", weight: 8.7 },
        { stockId: "s012", stockName: "HCL Technologies", weight: 7.4 },
      ]
    },
    {
      id: "mf005",
      name: "Kotak Banking ETF",
      type: "ETF",
      isin: "INF123D05IJ6",
      sector: "Banking",
      performance: 0.75,
      changePercent: 0.12,
      nav: 378.90,
      holdings: [
        { stockId: "s002", stockName: "HDFC Bank", weight: 25.3 },
        { stockId: "s013", stockName: "ICICI Bank", weight: 21.8 },
        { stockId: "s014", stockName: "SBI", weight: 15.4 },
      ]
    },
    {
      id: "mf006",
      name: "Nippon India Pharma Fund",
      type: "MutualFund",
      isin: "INF123D06KL7",
      sector: "Pharma",
      performance: 4.89,
      changePercent: 0.72,
      nav: 265.40,
      holdings: [
        { stockId: "s015", stockName: "Sun Pharma", weight: 12.5 },
        { stockId: "s016", stockName: "Dr Reddy's Labs", weight: 10.8 },
        { stockId: "s017", stockName: "Cipla", weight: 8.9 },
      ]
    },
    {
      id: "mf007",
      name: "Franklin India Smaller Companies Fund",
      type: "MutualFund",
      isin: "INF123D07MN8",
      sector: "Small Cap",
      performance: 6.12,
      changePercent: 1.05,
      nav: 48.75,
      holdings: [
        { stockId: "s018", stockName: "HDFC Bank", weight: 10.0 },
        { stockId: "s019", stockName: "ICICI Bank", weight: 9.5 },
        { stockId: "s020", stockName: "Tata Motors", weight: 8.0 },
      ]
    },
    {
      id: "mf008",
      name: "Mirae Asset Emerging Bluechip Fund",
      type: "MutualFund",
      isin: "INF123D08OP9",
      sector: "Large Cap",
      performance: 5.25,
      changePercent: 0.90,
      nav: 75.50,
      holdings: [
        { stockId: "s021", stockName: "Infosys", weight: 11.0 },
        { stockId: "s022", stockName: "TCS", weight: 10.0 },
        { stockId: "s023", stockName: "HCL Technologies", weight: 9.0 },
      ]
    },
    {
      id: "mf009",
      name: "Sundaram Select Focus Fund",
      type: "MutualFund",
      isin: "INF123D09QR0",
      sector: "Multi Cap",
      performance: 4.75,
      changePercent: 0.85,
      nav: 60.00,
      holdings: [
        { stockId: "s024", stockName: "Bajaj Finance", weight: 10.0 },
        { stockId: "s025", stockName: "Titan Company", weight: 9.0 },
        { stockId: "s026", stockName: "Reliance Industries", weight: 8.0 },
      ]
    },
    {
      id: "mf010",
      name: "UTI Nifty Index Fund",
      type: "MutualFund",
      isin: "INF123D10ST1",
      sector: "Index Fund",
      performance: 3.50,
      changePercent: 0.50,
      nav: 100.00,
      holdings: [
        { stockId: "s027", stockName: "Nifty", weight: 100.0 },
      ]
    }
  ];
};

export const fetchStocksData = async (): Promise<FinancialItem[]> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Mock data for stocks
  return [
    {
      id: "s001",
      name: "Reliance Industries",
      type: "Stock",
      ticker: "RELIANCE.NS",
      sector: "Energy",
      performance: 2.15,
      changePercent: 0.78,
      price: 2542.35
    },
    {
      id: "s002",
      name: "HDFC Bank",
      type: "Stock",
      ticker: "HDFCBANK.NS",
      sector: "Banking",
      performance: -0.58,
      changePercent: -0.23,
      price: 1598.45
    },
    {
      id: "s003",
      name: "Infosys",
      type: "Stock",
      ticker: "INFY.NS",
      sector: "Technology",
      performance: -1.85,
      changePercent: -0.92,
      price: 1432.80
    },
    {
      id: "s004",
      name: "Jyothy Labs",
      type: "Stock",
      ticker: "JYOTHYLAB.NS",
      sector: "FMCG",
      performance: 3.45,
      changePercent: 1.62,
      price: 321.75
    },
    {
      id: "s005",
      name: "Bajaj Finance",
      type: "Stock",
      ticker: "BAJFINANCE.NS",
      sector: "Finance",
      performance: -0.35,
      changePercent: -0.15,
      price: 6785.20
    },
    {
      id: "s006",
      name: "Titan Company",
      type: "Stock",
      ticker: "TITAN.NS",
      sector: "Consumer Durables",
      performance: 1.25,
      changePercent: 0.53,
      price: 2865.30
    },
    {
      id: "s007",
      name: "Tata Motors",
      type: "Stock",
      ticker: "TATAMOTORS.NS",
      sector: "Automobile",
      performance: 4.25,
      changePercent: 1.92,
      price: 765.85
    },
    {
      id: "s008",
      name: "IndiaMART",
      type: "Stock",
      ticker: "INDIAMART.NS",
      sector: "Technology",
      performance: -2.35,
      changePercent: -1.24,
      price: 8954.60
    },
    {
      id: "s009",
      name: "Hindustan Unilever",
      type: "Stock",
      ticker: "HINDUNILVR.NS",
      sector: "FMCG",
      performance: 1.50,
      changePercent: 0.75,
      price: 2500.00
    },
    {
      id: "s010",
      name: "Maruti Suzuki",
      type: "Stock",
      ticker: "MARUTI.NS",
      sector: "Automobile",
      performance: 2.00,
      changePercent: 0.50,
      price: 8000.00
    }
  ];
};

export const fetchMutualFundHoldings = async (fundId: string): Promise<FinancialItem['holdings']> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // In a real app, you would fetch this from the API based on the fund ID
  const funds = await fetchMutualFundsData();
  const fund = funds.find(fund => fund.id === fundId);
  
  return fund?.holdings || [];
};
