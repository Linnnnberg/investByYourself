import { useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { Dashboard } from "./components/Dashboard";
import { MarketInsights } from "./components/MarketInsights";
import { PositionList } from "./components/PositionList";
import { PlaceholderView } from "./components/PlaceholderView";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard />;
      case "market-insights":
        return <MarketInsights />;
      case "portfolio":
        return <PositionList />;
      case "analysis":
        return (
          <PlaceholderView
            title="Analysis"
            description="Advanced tools for technical and fundamental analysis."
          />
        );
      case "reports":
        return (
          <PlaceholderView
            title="Reports"
            description="Generate detailed performance and tax reports."
          />
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="h-screen flex bg-background">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="flex-1 flex flex-col">
        <Header />

        <main className="flex-1 overflow-auto bg-background">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}
