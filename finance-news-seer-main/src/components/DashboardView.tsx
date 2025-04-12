
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FinancialItem } from "@/types";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";
import { ArrowUpRight, ArrowDownRight, TrendingUp, TrendingDown } from "lucide-react";

interface DashboardViewProps {
  mutualFunds: FinancialItem[];
  stocks: FinancialItem[];
}

const DashboardView = ({ mutualFunds, stocks }: DashboardViewProps) => {
  const [view, setView] = useState<"mutualFunds" | "stocks">("mutualFunds");
  
  const renderPerformanceCard = (title: string, value: number, change: number) => (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-gray-500">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline">
          <div className="text-2xl font-bold">
            {typeof value === 'number' ? value.toFixed(2) : value}
          </div>
          <div className={`ml-2 text-sm flex items-center ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {change >= 0 ? (
              <>
                <ArrowUpRight size={16} className="mr-1" />
                +{change.toFixed(2)}%
              </>
            ) : (
              <>
                <ArrowDownRight size={16} className="mr-1" />
                {change.toFixed(2)}%
              </>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  // Prepare chart data
  const topPerformers = view === "mutualFunds" 
    ? mutualFunds.slice(0, 5).map(fund => ({ name: fund.name.slice(0, 15) + "...", value: fund.performance }))
    : stocks.slice(0, 5).map(stock => ({ name: stock.name.slice(0, 15) + "...", value: stock.performance }));

  const bottomPerformers = view === "mutualFunds"
    ? [...mutualFunds].sort((a, b) => a.performance - b.performance).slice(0, 5)
        .map(fund => ({ name: fund.name.slice(0, 15) + "...", value: fund.performance }))
    : [...stocks].sort((a, b) => a.performance - b.performance).slice(0, 5)
        .map(stock => ({ name: stock.name.slice(0, 15) + "...", value: stock.performance }));

  // Weekly performance data for nifty
  const weeklyData = [
    { day: "Mon", value: 18250 },
    { day: "Tue", value: 18300 },
    { day: "Wed", value: 18150 },
    { day: "Thu", value: 18200 },
    { day: "Fri", value: 18100 },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {renderPerformanceCard("Nifty 50", 18100.25, -0.53)}
        {renderPerformanceCard("Avg Mutual Fund", 12.45, 0.75)}
        {renderPerformanceCard("Banking Sector", 42530.68, -1.2)}
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Nifty Weekly Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={weeklyData}
                margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis domain={['auto', 'auto']} />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#3b82f6" activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
      
      <Tabs value={view} onValueChange={(v) => setView(v as "mutualFunds" | "stocks")}>
        <TabsList className="grid grid-cols-2 mb-4">
          <TabsTrigger value="mutualFunds">Mutual Funds</TabsTrigger>
          <TabsTrigger value="stocks">Stocks</TabsTrigger>
        </TabsList>
        
        <TabsContent value="mutualFunds">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="mr-2 text-green-600" />
                  Top Performing Funds
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={topPerformers}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#22c55e" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingDown className="mr-2 text-red-600" />
                  Bottom Performing Funds
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={bottomPerformers}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#ef4444" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        
        <TabsContent value="stocks">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="mr-2 text-green-600" />
                  Top Performing Stocks
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={topPerformers}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#22c55e" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingDown className="mr-2 text-red-600" />
                  Bottom Performing Stocks
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={bottomPerformers}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#ef4444" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DashboardView;
