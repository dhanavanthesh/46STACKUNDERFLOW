
import { FinancialItem, SearchQuery } from "@/types";

export const searchFinancialData = async (
  query: string,
  data: FinancialItem[],
  filters?: Partial<SearchQuery>
): Promise<FinancialItem[]> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // Process the query to extract relevant information
  const normalizedQuery = query.toLowerCase();
  
  // Extract potential instrument names from query
  const extractedNames = extractNamesFromQuery(normalizedQuery);
  
  // Filter data based on the extracted names and query terms
  return data.filter(item => {
    const itemName = item.name.toLowerCase();
    const itemSector = item.sector.toLowerCase();
    const itemType = item.type.toLowerCase();
    
    // Check for direct matches with name
    if (extractedNames.some(name => itemName.includes(name))) {
      return true;
    }
    
    // Check if query contains the item name
    if (normalizedQuery.includes(itemName)) {
      return true;
    }
    
    // Check for sector matches
    if (normalizedQuery.includes(itemSector)) {
      return true;
    }
    
    // Check for type matches (mutual fund, stock, etf)
    if (normalizedQuery.includes(itemType) || 
        (itemType === "mutualfund" && normalizedQuery.includes("fund"))) {
      return true;
    }
    
    // Apply any additional filters
    if (filters?.type && filters.type !== "All" && item.type !== filters.type) {
      return false;
    }
    
    return false;
  });
};

// Helper function to extract potential financial instrument names from the query
const extractNamesFromQuery = (query: string): string[] => {
  // List of common financial instrument names and companies
  const knownNames = [
    "nifty", "sensex", "hdfc", "sbi", "axis", "icici", "reliance", 
    "infosys", "tcs", "bajaj", "kotak", "jyothy", "labs", "tata", "motors",
    "adani", "zomato", "paytm", "gold", "oil", "byjus", "tata motors", "titan", "bajaj finance",
    "sun pharma", "dr reddys", "cipla", "indiamart", "kpit", "mastek", "hcl", "irctc"
  ];
  
  // Check for known names in the query
  const foundNames = knownNames.filter(name => query.includes(name));
  
  // Extract potential names based on capitalization (simplified approach)
  const words = query.split(/\s+/);
  const potentialNames = words.filter(word => 
    word.length > 2 && !["why", "did", "what", "happened", "to", "this", "week", "any", "the"].includes(word)
  );
  
  return [...foundNames, ...potentialNames];
};
