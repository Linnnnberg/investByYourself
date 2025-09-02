import { Card } from "./ui/card";

interface PlaceholderViewProps {
  title: string;
  description: string;
}

export function PlaceholderView({ title, description }: PlaceholderViewProps) {
  return (
    <div className="p-6">
      <Card className="p-12 text-center">
        <h2 className="text-xl font-semibold mb-2">{title}</h2>
        <p className="text-muted-foreground">{description}</p>
        <p className="text-sm text-muted-foreground mt-4">
          This feature will be implemented soon.
        </p>
      </Card>
    </div>
  );
}
