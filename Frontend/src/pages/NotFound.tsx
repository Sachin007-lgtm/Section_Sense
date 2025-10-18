import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { Scale, Home } from "lucide-react";
import { Button } from "@/components/ui/button";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-subtle">
      <div className="text-center max-w-md mx-auto px-4">
        <Scale className="h-20 w-20 text-muted-foreground mx-auto mb-8" />
        <h1 className="mb-4 text-6xl font-merriweather font-bold text-foreground">404</h1>
        <p className="mb-8 text-xl text-muted-foreground">
          The page you're looking for doesn't exist in our legal database.
        </p>
        <Button asChild className="bg-gradient-legal">
          <a href="/" className="inline-flex items-center">
            <Home className="h-4 w-4 mr-2" />
            Return to Home
          </a>
        </Button>
      </div>
    </div>
  );
};

export default NotFound;
