import { Search, User } from "lucide-react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";

export function Header() {
  return (
    <header className="bg-background border-b border-border px-6 py-4 flex items-center justify-between">
      <div className="flex-1 max-w-md relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
        <Input
          placeholder="Search companies..."
          className="pl-10 bg-input-background border-0"
        />
      </div>

      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm">
          New Portfolio
        </Button>
        <Button variant="outline" size="sm">
          Add to Watchlist
        </Button>
        <Button size="sm" className="w-8 h-8 p-0 rounded-full bg-primary text-primary-foreground">
          <User size={16} />
        </Button>
      </div>
    </header>
  );
}
