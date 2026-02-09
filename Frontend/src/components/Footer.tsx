import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="bg-muted border-t border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col items-center space-y-3">
          <div className="flex items-center space-x-4 text-sm">
            <Link 
              to="/privacy-policy" 
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Privacy Policy
            </Link>
            <span className="text-muted-foreground">•</span>
            <Link 
              to="/contact" 
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Contact
            </Link>
          </div>
          <p className="text-muted-foreground text-sm">
            © 2025 Section Sense | Built with AI for Legal Innovation
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;