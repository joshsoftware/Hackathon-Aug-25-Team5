'use client';

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Upload, FileText, CheckCircle, Clock, Loader2, Info } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const statusSteps = [
  { id: "parsing", label: "Document Parsing", icon: FileText },
  { id: "verification", label: "Verification", icon: CheckCircle },
  { id: "timeline", label: "Timeline Generated", icon: Clock },
];

export default function DocumentUpload() {
  // Use a mounted state to prevent hydration mismatch
  const [mounted, setMounted] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  // Ensure component is mounted before rendering interactive elements
  useEffect(() => {
    setMounted(true);
  }, []);

  const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', 'property_document');
    formData.append('description', 'Property document uploaded for analysis');

    try {
      setIsProcessing(true);
      setUploadProgress(0);
      setCurrentStep(0);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Use axios instead of fetch
      const response = await axios.post('/http://localhost:8000/document/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        // Optional: Add upload progress tracking
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percentCompleted);
          }
        },
      });

      clearInterval(progressInterval);

      // Axios automatically throws on non-2xx status codes
      const result = response.data;
      
      // Complete progress and steps
      setUploadProgress(100);
      setCurrentStep(3);
      
      toast.success('Document uploaded successfully!');
      setUploadedFile(file);
      
      // Reset after showing success
      setTimeout(() => {
        setIsProcessing(false);
        setUploadProgress(0);
        setCurrentStep(0);
        setUploadedFile(null);
      }, 3000);

    } catch (error) {
      console.error('Upload error:', error);
      
      // Handle axios errors
      if (axios.isAxiosError(error)) {
        if (error.response) {
          // Server responded with error status
          const errorMessage = error.response.data?.detail || `Upload failed: ${error.response.status}`;
          toast.error(errorMessage);
        } else if (error.request) {
          // Request was made but no response received
          toast.error('No response from server. Please check if the backend is running.');
        } else {
          // Something else happened
          toast.error('Upload failed: ' + error.message);
        }
      } else {
        // Non-axios error
        toast.error(error instanceof Error ? error.message : 'Upload failed');
      }
      
      setIsProcessing(false);
      setUploadProgress(0);
      setCurrentStep(0);
    }
  };

  const handleFileUpload = (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const file = files[0];
    if (!file.type.includes("pdf")) {
      toast.error("Please upload a PDF document.");
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      toast.error("File size must be less than 50MB.");
      return;
    }

    uploadFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  // Don't render interactive elements until mounted to prevent hydration mismatch
  if (!mounted) {
    return (
      <div className="bg-gradient-to-r from-gray-100 via-gray-50 to-white py-8 shadow-md w-full">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <div className="text-center space-y-4">
            <h1 className="text-3xl font-bold text-foreground">
              Document Upload & Processing
            </h1>
            <p className="text-lg text-muted-foreground">
              Upload your property documents for automated analysis and timeline generation
            </p>
          </div>
          
          {/* Loading placeholder */}
          <Card className="shadow-lg rounded-2xl overflow-hidden">
            <CardHeader>
              <CardTitle className="text-2xl">Upload Property Document</CardTitle>
              <CardDescription className="text-lg">
                Loading...
              </CardDescription>
            </CardHeader>
            <CardContent className="p-12 text-center">
              <Loader2 className="w-12 h-12 mx-auto text-gray-400 mb-4 animate-spin" />
              <p className="text-gray-500">Initializing...</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-gray-100 via-gray-50 to-white py-8 shadow-md w-full">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-bold text-foreground">
            Document Upload & Processing
          </h1>
          <p className="text-lg text-muted-foreground">
            Upload your property documents for automated analysis and timeline generation
          </p>
        </div>

        {/* Upload Area */}
        <Card className="shadow-lg rounded-2xl overflow-hidden">
          <CardHeader>
            <CardTitle className="text-2xl">Upload Property Document</CardTitle>
            <CardDescription className="text-lg">
              Drag and drop your property PDF document or click to browse
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div
              className={`
                border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300
                ${isDragOver ? "border-blue-500 bg-blue-50 shadow-lg" : "border-gray-300"}
                ${isProcessing ? "opacity-50 cursor-not-allowed" : "cursor-pointer hover:border-blue-500 hover:bg-blue-50 hover:shadow-md"}
              `}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => !isProcessing && document.getElementById("file-input")?.click()}
            >
              {uploadedFile ? (
                <div className="space-y-4">
                  <CheckCircle className="w-12 h-12 mx-auto text-green-500 mb-4" />
                  <h3 className="text-lg font-medium text-green-700 mb-2">Upload Complete!</h3>
                  <p className="text-green-600 mb-4">{uploadedFile.name}</p>
                </div>
              ) : (
                <>
                  <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium mb-2">Drop your document here</h3>
                  <p className="text-gray-500 mb-4">
                    Supports PDF files up to 50MB
                  </p>
                  <Button variant="outline" disabled={isProcessing}>
                    {isProcessing ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <FileText className="w-4 h-4 mr-2" />
                        Browse Files
                      </>
                    )}
                  </Button>
                </>
              )}
            </div>

            <input
              id="file-input"
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => handleFileUpload(e.target.files)}
              disabled={isProcessing}
            />

            {/* Progress Section - Show only when processing */}
            {isProcessing && (
              <div className="space-y-6">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Upload Progress</span>
                    <span className="text-sm text-gray-500">{uploadProgress}%</span>
                  </div>
                  <Progress value={uploadProgress} className="h-2" />
                </div>

                {/* Status Steps */}
                <div className="space-y-4">
                  <h4 className="text-sm font-medium text-gray-500">Processing Status</h4>
                  <div className="space-y-3">
                    {statusSteps.map((step, index) => {
                      const Icon = step.icon;
                      const isActive = index === currentStep;
                      const isCompleted = index < currentStep;
                      
                      return (
                        <div
                          key={step.id}
                          className={`
                            flex items-center space-x-3 p-3 rounded-lg transition-all duration-300
                            ${isActive ? "bg-blue-50 border border-blue-200" : ""}
                            ${isCompleted ? "bg-green-50" : ""}
                          `}
                        >
                          <div
                            className={`
                              w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300
                              ${isCompleted ? "bg-green-500 text-white" : ""}
                              ${isActive ? "bg-blue-500 text-white" : "bg-gray-200"}
                              ${!isActive && !isCompleted ? "text-gray-400" : ""}
                            `}
                          >
                            {isCompleted ? (
                              <CheckCircle className="w-4 h-4" />
                            ) : isActive ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Icon className="w-4 h-4" />
                            )}
                          </div>
                          <span
                            className={`
                              font-medium transition-all duration-300
                              ${isActive || isCompleted ? "text-gray-900" : "text-gray-500"}
                            `}
                          >
                            {step.label}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="p-6 bg-blue-50 border-blue-200">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <Info className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-medium text-blue-900 mb-1">Supported Documents</h3>
              <p className="text-sm text-blue-700 mb-3">
                We accept property documents including title deeds, property searches, 
                legal certificates, and related documentation in PDF format.
              </p>
              <ul className="text-sm text-blue-600 space-y-1">
                <li>• Maximum file size: 50MB per document</li>
                <li>• Multiple documents can be uploaded simultaneously</li>
                <li>• Documents are processed using bank-level encryption</li>
              </ul>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
} 
