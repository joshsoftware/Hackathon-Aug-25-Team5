'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calendar, Clock, MapPin, FileText, Users, AlertTriangle } from "lucide-react";
import { useRef, useState } from "react";

// Timeline data for different reports
const timelineData = {
  "Risk Assessment Q4 2023": [
    {
      id: 1,
      date: "January 1, 2023",
      title: "Portfolio Analysis Initiated",
      description: "Comprehensive review of all properties in portfolio",
      type: "analysis",
      details: "Portfolio size: 24 properties • Total value: $12.4M",
      icon: FileText,
    },
    {
      id: 2,
      date: "March 15, 2023",
      title: "Risk Assessment Phase",
      description: "Detailed risk evaluation for each property",
      type: "assessment",
      details: "Risk levels identified: Low (16), Medium (5), High (3)",
      icon: AlertTriangle,
    },
    {
      id: 3,
      date: "June 30, 2023",
      title: "Lien Analysis Complete",
      description: "All outstanding liens identified and categorized",
      type: "lien",
      details: "Total outstanding liens: $156K across 8 properties",
      icon: AlertTriangle,
    },
    {
      id: 4,
      date: "September 30, 2023",
      title: "Market Value Assessment",
      description: "Current market values compared to purchase prices",
      type: "valuation",
      details: "Average appreciation: 23% • Range: 8% to 45%",
      icon: MapPin,
    },
    {
      id: 5,
      date: "December 15, 2023",
      title: "Final Report Generated",
      description: "Comprehensive portfolio risk assessment complete",
      type: "report",
      details: "Report size: 2.4 MB • Recommendations: 12 action items",
      icon: FileText,
    },
  ],
  "123 Main Street - Individual Property Analysis": [
    {
      id: 1,
      date: "March 15, 2020",
      title: "Original Purchase",
      description: "Property acquired by John & Jane Smith",
      type: "purchase",
      details: "Purchase price: $485,000 • Mortgage: First National Bank",
      icon: Users,
    },
    {
      id: 2,
      date: "August 22, 2021",
      title: "Refinancing",
      description: "Mortgage refinanced with lower rate",
      type: "refinance",
      details: "New rate: 2.75% • Lender: Community Credit Union",
      icon: FileText,
    },
    {
      id: 3,
      date: "January 10, 2022",
      title: "Property Transfer",
      description: "Transferred to Smith Family Trust",
      type: "transfer",
      details: "Trust establishment for estate planning purposes",
      icon: Users,
    },
    {
      id: 4,
      date: "September 5, 2023",
      title: "Lien Recorded",
      description: "Contractor lien filed by ABC Construction",
      type: "lien",
      details: "Amount: $15,400 • Reason: Unpaid renovation work",
      icon: AlertTriangle,
    },
    {
      id: 5,
      date: "November 12, 2023",
      title: "Current Valuation",
      description: "Property assessed at $675,000",
      type: "valuation",
      details: "Market appreciation: 39% since purchase",
      icon: MapPin,
    },
  ],
  "Lien Analysis Summary - November 2023": [
    {
      id: 1,
      date: "November 1, 2023",
      title: "Lien Discovery Phase",
      description: "Systematic review of all property records",
      type: "discovery",
      details: "Properties reviewed: 24 • Liens found: 8",
      icon: FileText,
    },
    {
      id: 2,
      date: "November 15, 2023",
      title: "Lien Categorization",
      description: "Liens categorized by type and priority",
      type: "categorization",
      details: "Contractor liens: 5 • Tax liens: 2 • HOA liens: 1",
      icon: AlertTriangle,
    },
    {
      id: 3,
      date: "November 25, 2023",
      title: "Risk Assessment",
      description: "Each lien evaluated for risk level",
      type: "assessment",
      details: "High risk: 2 • Medium risk: 4 • Low risk: 2",
      icon: AlertTriangle,
    },
    {
      id: 4,
      date: "November 30, 2023",
      title: "Summary Report Complete",
      description: "Lien analysis summary report generated",
      type: "report",
      details: "Total outstanding: $156K • Report size: 856 KB",
      icon: FileText,
    },
  ],
};

const defaultTimelineEvents = [
  {
    id: 1,
    date: "March 15, 2020",
    title: "Original Purchase",
    description: "Property acquired by John & Jane Smith",
    type: "purchase",
    details: "Purchase price: $485,000 • Mortgage: First National Bank",
    icon: Users,
  },
  {
    id: 2,
    date: "August 22, 2021",
    title: "Refinancing",
    description: "Mortgage refinanced with lower rate",
    type: "refinance",
    details: "New rate: 2.75% • Lender: Community Credit Union",
    icon: FileText,
  },
  {
    id: 3,
    date: "January 10, 2022",
    title: "Property Transfer",
    description: "Transferred to Smith Family Trust",
    type: "transfer",
    details: "Trust establishment for estate planning purposes",
    icon: Users,
  },
  {
    id: 4,
    date: "September 5, 2023",
    title: "Lien Recorded",
    description: "Contractor lien filed by ABC Construction",
    type: "lien",
    details: "Amount: $15,400 • Reason: Unpaid renovation work",
    icon: AlertTriangle,
  },
  {
    id: 5,
    date: "November 12, 2023",
    title: "Current Valuation",
    description: "Property assessed at $675,000",
    type: "valuation",
    details: "Market appreciation: 39% since purchase",
    icon: MapPin,
  },
];

const getTypeColor = (type: string) => {
  switch (type) {
    case "purchase":
      return "bg-teal/10 text-teal border-teal/20";
    case "refinance":
      return "bg-primary/10 text-primary border-primary/20";
    case "transfer":
      return "bg-secondary text-secondary-foreground border-border";
    case "lien":
      return "bg-warning/10 text-warning border-warning/20";
    case "valuation":
      return "bg-success/10 text-success border-success/20";
    case "analysis":
      return "bg-blue/10 text-blue border-blue/20";
    case "assessment":
      return "bg-purple/10 text-purple border-purple/20";
    case "discovery":
      return "bg-indigo/10 text-indigo border-indigo/20";
    case "categorization":
      return "bg-orange/10 text-orange border-orange/20";
    case "report":
      return "bg-green/10 text-green border-green/20";
    default:
      return "bg-muted text-muted-foreground border-border";
  }
};

export default function Dashboard() {
  const [selectedReport, setSelectedReport] = useState<string | null>(null);
  const timelineRef = useRef<HTMLDivElement>(null);
  
  const currentTimelineEvents = selectedReport 
    ? timelineData[selectedReport as keyof typeof timelineData] || defaultTimelineEvents
    : defaultTimelineEvents;

  const handleViewTimeline = (reportTitle: string) => {
    setSelectedReport(reportTitle);
    
    // Scroll to timeline section
    if (timelineRef.current) {
      timelineRef.current.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }
  };

  const getTimelineTitle = () => {
    if (selectedReport) {
      return `Timeline for: ${selectedReport}`;
    }
    return "Property History Timeline";
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Reports Section */}
        <div className="max-w-6xl mx-auto mt-12">
          <Card className="shadow-medium">
            <CardHeader>
              <CardTitle className="text-chart-2 text-2xl">Recent Analysis Reports</CardTitle>
              <CardDescription>
                Latest generated property legal reports and documentation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  {
                    title: "Comprehensive Portfolio Risk Assessment Q4 2023",
                    type: "Portfolio Report",
                    date: "December 15, 2023",
                    size: "2.4 MB",
                    status: "Ready"
                  },
                  {
                    title: "123 Main Street - Individual Property Analysis",
                    type: "Property Report",
                    date: "December 10, 2023",
                    size: "1.1 MB",
                    status: "Ready"
                  },
                  {
                    title: "Lien Analysis Summary - November 2023",
                    type: "Summary Report",
                    date: "November 30, 2023",
                    size: "856 KB",
                    status: "Ready"
                  },
                ].map((report, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 rounded-lg border bg-card hover:shadow-soft transition-smooth  hover:border-chart-2/30"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <FileText className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h4 className="font-medium text-foreground">{report.title}</h4>
                        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                          <span>{report.type}</span>
                          <span>•</span>
                          <span>{report.date}</span>
                          <span>•</span>
                          <span>{report.size}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Button 
                        variant="outline" 
                        size="lg"
                        className="transition-colors cursor-pointer group"
                        onClick={() => handleViewTimeline(report.title)}
                      >
                        <Clock className="w-4 h-4 mr-2" />
                        <span className="group-hover:cursor-pointer">View Timeline</span>
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Header */}
        <div className="text-center space-y-4" ref={timelineRef}>
          <h1 className="text-3xl font-bold text-foreground">
            Property Timeline Visualization
          </h1>
          <p className="text-lg text-muted-foreground">
            Complete chronological history of 123 Main Street, Anytown, ST 12345
          </p>
        </div>

        {/* Timeline Events */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="shadow-medium">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>{getTimelineTitle()}</CardTitle>
                </div>
                <Button 
                  variant="outline" 
                  size="lg"
                  className="transition-colors cursor-pointer hover:cursor-pointer"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Export Report
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="relative">
                {/* Timeline line */}
                <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border"></div>
                
                {currentTimelineEvents.map((event, index) => {
                  const Icon = event.icon;
                  return (
                    <div key={event.id} className="relative flex items-start space-x-6 pb-8">
                      {/* Timeline dot */}
                      <div className="relative z-10 flex items-center justify-center w-12 h-12 rounded-full bg-card border-2 border-primary shadow-soft">
                        <Icon className="w-5 h-5 text-primary" />
                      </div>
                      
                      {/* Event content */}
                      <div className="flex-1 min-w-0">
                        <div className="p-4 rounded-lg border bg-card shadow-soft hover:shadow-medium transition-smooth">
                          <div className="flex items-start justify-between mb-3">
                            <div className="space-y-1">
                              <h3 className="font-semibold text-foreground">{event.title}</h3>
                              <p className="text-sm text-chart-3 flex items-center font-medium bg-secondary px-2 py-1 rounded-md border">
                                <Calendar className="w-4 h-4 mr-1 text-chart-3" />
                                {event.date}
                              </p>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Badge variant="outline" className={`${getTypeColor(event.type)} rounded-2xl px-3 py-1.5 text-sm font-medium`}>
                                {event.type}
                              </Badge>
                            </div>
                          </div>
                          
                          <p className="text-foreground mb-2">{event.description}</p>
                          <p className="text-sm text-muted-foreground">{event.details}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
