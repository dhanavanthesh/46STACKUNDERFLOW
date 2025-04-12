
import { Loader2 } from "lucide-react";

const LoadingState = () => {
  return (
    <div className="min-h-[300px] flex flex-col items-center justify-center">
      <Loader2 className="h-8 w-8 text-blue-500 animate-spin mb-2" />
      <p className="text-gray-500">Loading data...</p>
    </div>
  );
};

export default LoadingState;
