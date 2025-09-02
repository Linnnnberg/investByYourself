import { Card } from "./ui/card";
import { ExternalLink, Clock } from "lucide-react";

interface NewsItem {
  title: string;
  summary: string;
  source: string;
  publishedAt: string;
  category: string;
  url?: string;
}

interface MarketNewsProps {
  news: NewsItem[];
}

export function MarketNews({ news }: MarketNewsProps) {
  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

    if (diffInHours < 1) {
      return "Just now";
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays}d ago`;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'market':
        return 'bg-blue-100 text-blue-800';
      case 'earnings':
        return 'bg-green-100 text-green-800';
      case 'economic':
        return 'bg-purple-100 text-purple-800';
      case 'company':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Market News</h3>
        <button className="text-sm text-blue-600 hover:text-blue-700">
          View All News →
        </button>
      </div>

      <div className="space-y-4">
        {news.map((item, index) => (
          <div key={index} className="border-b border-gray-100 pb-4 last:border-b-0 last:pb-0">
            <div className="flex items-start gap-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(item.category)}`}>
                    {item.category}
                  </span>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="w-3 h-3" />
                    {formatTimeAgo(item.publishedAt)}
                  </div>
                </div>

                <h4 className="font-medium text-sm mb-2 leading-snug">{item.title}</h4>
                <p className="text-sm text-muted-foreground mb-2 line-clamp-2">{item.summary}</p>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">{item.source}</span>
                  {item.url && (
                    <button className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700">
                      Read more <ExternalLink className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
