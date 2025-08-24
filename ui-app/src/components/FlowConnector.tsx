import { Badge } from "@/components/ui/badge";
import { User, MapPin, Calendar, DollarSign } from "lucide-react";

interface Transaction {
  id: string;
  year: number;
  seller: string;
  buyer: string;
  location: string;
  amount: string;
  documentRef: string;
  hasConflict?: boolean;
  conflictType?: string;
}

interface FlowchartNodeProps {
  transaction: Transaction;
  focusedPerson: string;
  onPersonClick: (person: string) => void;
  isStartNode: boolean;
}

export const FlowchartNode = ({ 
  transaction, 
  focusedPerson, 
  onPersonClick, 
  isStartNode 
}: FlowchartNodeProps) => {
  const isFocused = transaction.seller === focusedPerson || transaction.buyer === focusedPerson;
  const hasConflict = transaction.hasConflict;

  return (
    <div className={`relative p-4 rounded-lg border-2 transition-all duration-200 ${
      isFocused 
        ? 'border-primary bg-primary/5 shadow-lg' 
        : hasConflict 
          ? 'border-warning bg-warning/5' 
          : 'border-border bg-card'
    } ${isStartNode ? 'ring-2 ring-primary/20' : ''}`}>
      
      {/* Year Badge */}
      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
        <Badge variant="secondary" className="text-xs font-bold">
          {transaction.year}
        </Badge>
      </div>

      {/* Transaction Content */}
      <div className="space-y-3">
        {/* Seller */}
        <div className="flex items-center gap-2">
          <User className="w-4 h-4 text-muted-foreground" />
          <button
            onClick={() => onPersonClick(transaction.seller)}
            className={`text-sm font-medium hover:underline transition-colors ${
              transaction.seller === focusedPerson ? 'text-primary' : 'text-foreground'
            }`}
          >
            {transaction.seller}
          </button>
        </div>

        {/* Arrow */}
        <div className="flex justify-center">
          <div className="w-6 h-0.5 bg-border"></div>
          <div className="w-0 h-0 border-l-4 border-l-transparent border-r-4 border-r-transparent border-t-2 border-t-border ml-1"></div>
        </div>

        {/* Buyer */}
        <div className="flex items-center gap-2">
          <User className="w-4 h-4 text-muted-foreground" />
          <button
            onClick={() => onPersonClick(transaction.buyer)}
            className={`text-sm font-medium hover:underline transition-colors ${
              transaction.buyer === focusedPerson ? 'text-primary' : 'text-foreground'
            }`}
          >
            {transaction.buyer}
          </button>
        </div>

        {/* Transaction Details */}
        <div className="pt-2 border-t border-border/50 space-y-2 text-xs">
          <div className="flex items-center gap-2">
            <MapPin className="w-3 h-3 text-muted-foreground" />
            <span className="text-muted-foreground truncate">{transaction.location}</span>
          </div>
          <div className="flex items-center gap-2">
            <DollarSign className="w-3 h-3 text-success" />
            <span className="font-semibold text-success">{transaction.amount}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="w-3 h-3 text-muted-foreground" />
            <span className="text-muted-foreground">{transaction.documentRef}</span>
          </div>
        </div>

        {/* Conflict Indicator */}
        {hasConflict && (
          <div className="absolute -top-2 -right-2">
            <div className="w-4 h-4 bg-warning rounded-full flex items-center justify-center">
              <span className="text-xs text-warning-foreground font-bold">!</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

interface FlowConnectorProps {
  hasConflict: boolean;
  isActive: boolean;
}

export const FlowConnector = ({ hasConflict, isActive }: FlowConnectorProps) => {
  return (
    <div className="w-0.5 h-8 mx-auto my-2 relative">
      {/* Main line */}
      <div className={`w-full h-full transition-colors duration-200 ${
        hasConflict 
          ? 'bg-warning' 
          : isActive 
            ? 'bg-primary' 
            : 'bg-border'
      }`}></div>
      
      {/* Connection dots */}
      <div className={`absolute top-0 left-1/2 transform -translate-x-1/2 w-2 h-2 rounded-full ${
        hasConflict 
          ? 'bg-warning' 
          : isActive 
            ? 'bg-primary' 
            : 'bg-border'
      }`}></div>
      <div className={`absolute bottom-0 left-1/2 transform -translate-x-1/2 w-2 h-2 rounded-full ${
        hasConflict 
          ? 'bg-warning' 
          : isActive 
            ? 'bg-primary' 
            : 'bg-border'
      }`}></div>
    </div>
  );
}; 