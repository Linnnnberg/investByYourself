import { Search, Upload, Filter, BarChart3 } from "lucide-react";
import { Card } from "./ui/card";

interface QuickActionsProps {
  onAction: (action: string) => void;
}

export function QuickActions({ onAction }: QuickActionsProps) {
  const actions = [
    {
      id: "search",
      title: "Search Companies",
      icon: Search,
      description: "Find stocks and companies"
    },
    {
      id: "import",
      title: "Import Portfolio",
      icon: Upload,
      description: "Upload your existing data"
    },
    {
      id: "screener",
      title: "Stock Screener",
      icon: Filter,
      description: "Filter stocks by criteria"
    },
    {
      id: "report",
      title: "Performance Report",
      icon: BarChart3,
      description: "View detailed analytics"
    }
  ];

  return (
    <div>
      <h2 className="text-xl font-semibold mb-6">Quick Actions</h2>

      <div className="grid grid-cols-4 gap-4">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <Card
              key={action.id}
              className="p-6 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => onAction(action.id)}
            >
              <div className="flex flex-col items-center text-center gap-3">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <Icon className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium text-sm">{action.title}</h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    {action.description}
                  </p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
