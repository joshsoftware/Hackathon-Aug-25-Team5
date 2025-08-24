import { Badge } from "@/components/ui/badge";
import { User, MapPin, Calendar, DollarSign } from "lucide-react";

interface Transaction {
  id: string;
  year: number;
  seller: string;
  buyer: string;
<<<<<<< Updated upstream
  location: string;
  amount: string;
=======
>>>>>>> Stashed changes
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
    <div className={`relative p-6 rounded-lg border-2 transition-all duration-200 ${
      hasConflict 
        ? 'border-red-500 bg-red-50 shadow-lg' 
        : isFocused 
          ? 'border-primary bg-primary/5 shadow-lg' 
          : 'border-border bg-card'
    } ${isStartNode ? 'ring-2 ring-primary/20' : ''}`}>
      
      {/* Year Badge */}
      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
        <Badge variant="secondary" className="text-sm font-bold px-3 py-1">
          {transaction.year}
        </Badge>
      </div>

      {/* Transaction Content */}
      <div className="space-y-4">
        {/* Seller */}
        <div className="flex items-center gap-3">
          <User className="w-5 h-5 text-muted-foreground" />
          <button
            onClick={() => onPersonClick(transaction.seller)}
            className={`text-base font-medium hover:underline transition-colors ${
              transaction.seller === focusedPerson ? 'text-primary' : 'text-foreground'
            }`}
          >
            {transaction.seller}
          </button>
        </div>

        {/* Arrow */}
        <div className="flex justify-center">
          <div className="w-8 h-0.5 bg-border"></div>
          <div className="w-0 h-0 border-l-5 border-l-transparent border-r-5 border-r-transparent border-t-2 border-t-border ml-1"></div>
        </div>

        {/* Buyer */}
        <div className="flex items-center gap-3">
          <User className="w-5 h-5 text-muted-foreground" />
          <button
            onClick={() => onPersonClick(transaction.buyer)}
            className={`text-base font-medium hover:underline transition-colors ${
              transaction.buyer === focusedPerson ? 'text-primary' : 'text-foreground'
            }`}
          >
            {transaction.buyer}
          </button>
        </div>

        {/* Transaction Details */}
        <div className="pt-3 border-t border-border/50 space-y-3 text-sm">
<<<<<<< Updated upstream
          <div className="flex items-center gap-3">
            <MapPin className="w-4 h-4 text-muted-foreground" />
            <span className="text-muted-foreground truncate">{transaction.location}</span>
          </div>
          <div className="flex items-center gap-3">
            <DollarSign className="w-4 h-4 text-success" />
            <span className="font-semibold text-success">{transaction.amount}</span>
          </div>
=======
          
>>>>>>> Stashed changes
          <div className="flex items-center gap-3">
            <Calendar className="w-4 h-4 text-muted-foreground" />
            <span className="text-muted-foreground">{transaction.documentRef}</span>
          </div>
        </div>

        {/* Conflict Indicator */}
        {hasConflict && (
          <div className="absolute -top-2 -right-2">
            <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
              <span className="text-sm text-white font-bold">!</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};