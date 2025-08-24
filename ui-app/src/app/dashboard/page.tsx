'use client';

import { useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  ArrowLeft, 
  AlertTriangle, 
  User, 
  MapPin, 
  Calendar,
  DollarSign,
  FileText,
  Users,
  TrendingUp,
  FileText as FileTextIcon,
  ScrollText,
  Clock
} from "lucide-react";
import { FlowchartNode } from "@/components/FlowchartNode";
import { FlowConnector } from "@/components/FlowConnector";

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
  divertedTransactions?: Transaction[];
}

interface UploadedDocument {
  id: string;
  name: string;
  type: string;
  uploadDate: string;
  status: 'processed' | 'processing' | 'error';
  transactionCount: number;
  hasConflicts: boolean;
}

const Timeline = () => {
<<<<<<< Updated upstream
  const [focusedPerson, setFocusedPerson] = useState<string>("John Smith");
  const timelineRef = useRef<HTMLDivElement>(null);

  const transactions: Transaction[] = [
    {
      id: "1",
      year: 2010,
      seller: "Original Owner",
      buyer: "John Smith",
      location: "123 Oak Street, Downtown",
      amount: "$450,000",
      documentRef: "DOC-2010-001"
    },
    {
      id: "2", 
      year: 2013,
      seller: "John Smith",
      buyer: "Sarah Johnson",
      location: "123 Oak Street, Downtown",
      amount: "$520,000",
      documentRef: "DOC-2013-045"
    },
    {
      id: "3",
      year: 2016,
      seller: "Sarah Johnson", 
      buyer: "Michael Brown",
      location: "123 Oak Street, Downtown",
      amount: "$680,000",
      documentRef: "DOC-2016-089",
      hasConflict: true,
      conflictType: "Overlapping transaction period",
      divertedTransactions: [
        {
          id: "3a",
          year: 2016,
          seller: "Sarah Johnson",
          buyer: "Lisa Anderson",
          location: "123 Oak Street, Downtown",
          amount: "$675,000",
          documentRef: "DOC-2016-089",
          hasConflict: true,
          conflictType: "Diverted transaction"
        }
      ]
    },
    {
      id: "5",
      year: 2022,
      seller: "David Wilson",
      buyer: "Final Owner",
      location: "123 Oak Street, Downtown", 
      amount: "$820,000",
      documentRef: "DOC-2022-203"
=======
  const [focusedPerson, setFocusedPerson] = useState<string>("Venktesh Developers");
  const timelineRef = useRef<HTMLDivElement>(null);

  const transactions: Transaction[] = [
    {
      id: "1",
      year: 2009,
      seller: "Venktesh Developers",
      buyer: "SR Developers",
      documentRef: "18-03-2009"
    },
    {
      id: "2", 
      year: 2009,
      seller: "SR Developers",
      buyer: "Vivek Vidyasagar",
      documentRef: "17-12-2009"
    },
    {
      id: "3", 
      year: 2011,
      seller: "Vivek Vidyasagar",
      buyer: "SR Developers",
      documentRef: "25-01-2011"
    },
    {
      id: "3",
      year: 2011,
      seller: "SR Developers", 
      buyer: "Shweta Dhiren",
      documentRef: "28-01-2011",
      hasConflict: true,
      conflictType: "Overlapping transaction period",
      divertedTransactions: [
        {
          id: "3a",
          year: 2011,
          seller: "SR Developers",
          buyer: "Vinayak Behere",
          documentRef: "07-12-2011",
          hasConflict: true,
          conflictType: "Diverted transaction"
        }
      ]
    },
    {
      id: "5",
      year: 2014,
      seller: "Vinayak Behere",
      buyer: "Rental Agreement Doc",
      documentRef: "04-10-2014"
    },
    {
      id: "5",
      year: 2021,
      seller: "Vinayak Behere",
      buyer: "Amit K & Shravani P",
      documentRef: "02-07-2021"
>>>>>>> Stashed changes
    }
  ];

  // Sample uploaded documents data
  const uploadedDocuments: UploadedDocument[] = [
    {
      id: "doc1",
<<<<<<< Updated upstream
      name: "Property_Deed_2010-2022.pdf",
      type: "Property Deed",
      uploadDate: "2024-01-15",
      status: 'processed',
      transactionCount: 5,
=======
      name: "Index-II.pdf",
      type: "Property Deed",
      uploadDate: "23-08-2025",
      status: 'processed',
      transactionCount: 6,
>>>>>>> Stashed changes
      hasConflicts: true
    },
    {
      id: "doc2",
      name: "Land_Registry_2016.pdf",
      type: "Land Registry",
      uploadDate: "2024-01-14",
      status: 'processed',
      transactionCount: 3,
      hasConflicts: false
    },
    {
      id: "doc3",
      name: "Property_Transfer_2019.pdf",
      type: "Property Transfer",
      uploadDate: "2024-01-13",
      status: 'processing',
      transactionCount: 0,
      hasConflicts: false
    },
    {
      id: "doc4",
      name: "Title_Deed_2013.pdf",
      type: "Title Deed",
      uploadDate: "2024-01-12",
      status: 'processed',
      transactionCount: 2,
      hasConflicts: false
    }
  ];

  const conflicts = transactions.filter(t => t.hasConflict);
  const focusedTransactions = transactions.filter(t => 
    t.seller === focusedPerson || t.buyer === focusedPerson
  );

  const scrollToTimeline = () => {
    timelineRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processed':
        return '✓';
      case 'processing':
        return '⏳';
      case 'error':
        return '✗';
      default:
        return '?';
    }
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold">Property Transaction Timeline</h1>
            <p className="text-muted-foreground">13-year ownership chain analysis</p>
          </div>
        </div>

        {/* Uploaded Documents Section */}
        <Card className="bg-gradient-to-br from-slate-50 to-gray-50 border-2 border-slate-200 shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-slate-900">
              <FileTextIcon className="h-6 w-6 text-slate-600" />
              <span className="text-xl">Uploaded Documents</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <Card 
              className="cursor-pointer hover:shadow-lg transition-all duration-200 border-2 hover:border-blue-300 bg-white w-full"
              onClick={scrollToTimeline}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <FileTextIcon className="w-6 h-6 text-blue-600" />
                  </div>
                  <Badge 
                    variant="outline" 
                    className={`text-sm px-3 py-1 ${getStatusColor(uploadedDocuments[0].status)}`}
                  >
                    {getStatusIcon(uploadedDocuments[0].status)} {uploadedDocuments[0].status}
                  </Badge>
                </div>
                
                <h4 className="font-bold text-xl mb-2 text-gray-900">
                  {uploadedDocuments[0].name}
                </h4>
                
                <div className="grid md:grid-cols-3 gap-4 text-base text-gray-600 mb-3">
                  <div className="flex items-center gap-2">
                    <ScrollText className="w-5 h-5" />
                    <span className="font-medium">{uploadedDocuments[0].type}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-5 h-5" />
                    <span className="font-medium">{uploadedDocuments[0].uploadDate}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    <span className="font-medium">{uploadedDocuments[0].transactionCount} transactions</span>
                  </div>
                </div>

                {uploadedDocuments[0].hasConflicts && (
                  <div className="mb-3">
                    <Badge variant="outline" className="bg-red-50 text-red-700 border-red-300 text-sm px-3 py-1">
                      <AlertTriangle className="w-4 h-4 mr-2" />
                      Conflicts detected
                    </Badge>
                  </div>
                )}

                <div className="flex justify-end">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 text-base px-4 py-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      scrollToTimeline();
                    }}
                  >
                    View Timeline →
                  </Button>
                </div>
              </CardContent>
            </Card>
          </CardContent>
        </Card>

        {/* Flowchart Timeline */}
        <div ref={timelineRef} className="lg:col-span-3">
          <Card className="card-elegant bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 shadow-lg">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center justify-between text-blue-900">
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-6 w-6 text-blue-600" />
                  <span className="text-xl">Property Transaction Flow</span>
                </div>
                <div className="flex gap-2">
                  <Badge variant="outline" className="text-lg bg-blue-100 border-blue-300 text-blue-700">
                    <Users className="h-3 w-3 mr-1" />
                    Focus: {focusedPerson}
                  </Badge>
                  <Badge variant="outline" className="text-lg bg-indigo-100 border-indigo-300 text-indigo-700">
                    {transactions.length} Transactions
                  </Badge>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-8">
              {/* Flowchart Layout */}
              <div className="max-w-6xl mx-auto">
                {/* Legend */}
                <div className="mb-8 p-6 bg-white/70 rounded-xl border border-blue-200 shadow-sm">
                  <h4 className="font-semibold mb-3 text-sm text-blue-800">How to read this timeline:</h4>
                  <div className="grid md:grid-cols-4 gap-6 text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
                      <span className="text-blue-700">Focused person transactions</span>
                    </div>
                    <div className="flex items-center gap-2">
<<<<<<< Updated upstream
                      <div className="w-4 h-4 bg-orange-500 rounded-full"></div>
                      <span className="text-orange-700">Conflicted transactions</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                      <span className="text-red-700">Diverted transactions</span>
=======
                      <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                      <span className="text-red-700">Conflicted transactions</span>
>>>>>>> Stashed changes
                    </div>
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-blue-600" />
                      <span className="text-blue-700">Click any person to focus</span>
                    </div>
                  </div>
                </div>

                {/* Transaction Flow with Diverted Transactions */}
                <div className="space-y-0">
                  {transactions.map((transaction, index) => {
                    const isFocused = transaction.seller === focusedPerson || transaction.buyer === focusedPerson;
                    const nextTransaction = transactions[index + 1];
                    const hasConnectionConflict = nextTransaction?.hasConflict || transaction.hasConflict;
                    const hasDivertedTransactions = transaction.divertedTransactions && transaction.divertedTransactions.length > 0;
                    
                    return (
                      <div key={transaction.id} className="flex flex-col items-center">
                        {/* Main Transaction Node */}
                        <div className="flex items-center gap-8">
                          {/* Main Transaction */}
                          <FlowchartNode
                            transaction={transaction}
                            focusedPerson={focusedPerson}
                            onPersonClick={setFocusedPerson}
                            isStartNode={index === 0}
                          />
                          
                          {/* Diverted Transactions */}
                          {hasDivertedTransactions && (
                            <div className="flex flex-col gap-4">
                              {transaction.divertedTransactions!.map((diverted, divertedIndex) => (
                                <div key={diverted.id} className="flex items-center gap-4">
                                  {/* Diverted Transaction Node */}
                                  <FlowchartNode
                                    transaction={diverted}
                                    focusedPerson={focusedPerson}
                                    onPersonClick={setFocusedPerson}
                                    isStartNode={false}
                                  />
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                        
                        {/* Connection to Next Transaction */}
                        {index < transactions.length - 1 && (
                          <FlowConnector
                            hasConflict={hasConnectionConflict || false}
                            isActive={isFocused}
                          />
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-8">
          {/* Conflict Analysis */}
        </div>
      </div>
    </div>
  );
};

export default Timeline;