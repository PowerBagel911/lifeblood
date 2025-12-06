import { useState } from 'react';
import { Heart, MessageSquare, FileText, AlertTriangle, AlertCircle, Loader2 } from 'lucide-react';
import { Message, ResponseMode, Citation } from '../types';
import { apiClient, APIError } from '../app/api/client';
import ChatBox from './ChatBox';
import SourcesPanel from './SourcesPanel';

const ChatPage = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCitations, setSelectedCitations] = useState<Citation[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleSendMessage = async (question: string, mode: ResponseMode) => {
    setIsLoading(true);
    setError(null);
    
    // Add question to messages immediately with loading state
    const tempId = Date.now().toString();
    const loadingMessage: Message = {
      id: tempId,
      question,
      answer: '⏳ Processing your question with AI...',
      citations: [],
      mode,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, loadingMessage]);
    setSelectedCitations([]);
    
    try {
      // Call the real backend API
      const response = await apiClient.ask(question, mode, 5);
      
      // Convert API response to Message format
      const message: Message = {
        id: response.trace_id,
        question: response.question,
        answer: response.answer,
        citations: response.citations,
        mode: response.mode,
        timestamp: new Date()
      };

      // Replace loading message with actual response
      setMessages(prev => prev.map(msg => 
        msg.id === tempId ? message : msg
      ));
      setSelectedCitations(response.citations);
      
    } catch (error) {
      console.error('Error asking question:', error);
      
      let errorMessage = 'An unexpected error occurred';
      let traceId: string | undefined;

      if (error instanceof APIError) {
        errorMessage = error.message;
        traceId = error.traceId;
      }

      // Replace loading message with error
      const errorMessageObject: Message = {
        id: traceId || tempId,
        question,
        answer: `❌ Error: ${errorMessage}`,
        citations: [],
        mode,
        timestamp: new Date()
      };

      setMessages(prev => prev.map(msg => 
        msg.id === tempId ? errorMessageObject : msg
      ));
      setError(errorMessage);
      setSelectedCitations([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleIngestDocuments = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await apiClient.ingest();
      
      // Add system message about successful ingestion
      const systemMessage: Message = {
        id: result.trace_id,
        question: 'System: Document Ingestion',
        answer: `✅ Successfully loaded ${result.indexed_docs} documents and created ${result.indexed_chunks} chunks. You can now ask questions about the medical documentation.`,
        citations: [],
        mode: 'general',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, systemMessage]);
      
    } catch (error) {
      console.error('Error ingesting documents:', error);
      
      let errorMessage = 'Failed to load documents';
      if (error instanceof APIError) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMessageClick = (message: Message) => {
    setSelectedCitations(message.citations);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <Heart className="h-8 w-8 text-blood-red-600" />
                <h1 className="text-xl font-bold text-gray-900">
                  Lifeblood Operations Assistant
                </h1>
              </div>
              <div className="hidden sm:block">
                <span className="px-2 py-1 text-xs font-medium bg-blood-red-100 text-blood-red-700 rounded-full">
                  Medical AI Assistant
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <MessageSquare className="h-4 w-4" />
                <span>{messages.length} conversations</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <FileText className="h-4 w-4" />
                <span>{selectedCitations.length} sources</span>
              </div>
              {/* Connection Status */}
              <div className="flex items-center space-x-2 text-xs">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-gray-600">API Connected</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-center space-x-3">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm text-red-800">
                  <strong>Connection Error:</strong> {error}
                </p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-600 hover:text-red-800 text-sm underline"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.length === 0 ? (
                <div className="text-center py-12">
                  <Heart className="h-16 w-16 mx-auto text-blood-red-300 mb-4" />
                  <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                    Welcome to Lifeblood Operations Assistant
                  </h2>
                  <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                    Ask questions about blood donation procedures, donor eligibility, 
                    safety protocols, and medical operations. Get evidence-based answers 
                    with source citations.
                  </p>
                  
                  <div className="grid md:grid-cols-3 gap-4 max-w-3xl mx-auto mb-8">
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <h3 className="font-medium text-gray-900 mb-2">Example Questions</h3>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• What are donor eligibility requirements?</li>
                        <li>• How should plasma be handled?</li>
                        <li>• What safety protocols should be followed?</li>
                      </ul>
                    </div>
                    
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <h3 className="font-medium text-gray-900 mb-2">Response Modes</h3>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• <strong>General:</strong> Concise answers</li>
                        <li>• <strong>Checklist:</strong> Step-by-step</li>
                        <li>• <strong>Plain English:</strong> Simplified</li>
                      </ul>
                    </div>
                    
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <h3 className="font-medium text-gray-900 mb-2">Citations</h3>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• Source documents shown</li>
                        <li>• Relevance scores provided</li>
                        <li>• Evidence-based responses</li>
                      </ul>
                    </div>
                  </div>
                  
                  {/* Quick Start Actions */}
                  <div className="bg-blue-50 rounded-lg p-4 max-w-md mx-auto">
                    <h3 className="font-medium text-blue-900 mb-2">First Time Setup</h3>
                    <p className="text-sm text-blue-800 mb-3">
                      Make sure documents are loaded into the knowledge base first.
                    </p>
                    <button
                      onClick={handleIngestDocuments}
                      disabled={isLoading}
                      className="w-full px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium
                               hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                    >
                      Load Documents
                    </button>
                  </div>
                </div>
              ) : (
                messages.map((message) => {
                  const isSystemMessage = message.question.startsWith('System:');
                  const isErrorMessage = message.answer.startsWith('❌ Error:');
                  const isLoadingMessage = message.answer.startsWith('⏳ Processing');
                  
                  return (
                    <div
                      key={message.id}
                      onClick={() => !isSystemMessage && handleMessageClick(message)}
                      className={`rounded-lg shadow-sm border p-6 transition-all ${
                        isSystemMessage 
                          ? 'bg-blue-50 border-blue-200 cursor-default' 
                          : isErrorMessage
                            ? 'bg-red-50 border-red-200 cursor-default'
                          : isLoadingMessage
                            ? 'bg-gray-50 border-gray-300 cursor-default animate-pulse'
                            : 'bg-white border-gray-200 cursor-pointer hover:shadow-md'
                      }`}
                    >
                      {/* Question */}
                      <div className="mb-4">
                        <div className="flex items-start space-x-3">
                          {isSystemMessage ? (
                            <FileText className="h-5 w-5 text-blue-600 mt-0.5" />
                          ) : isErrorMessage ? (
                            <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                          ) : isLoadingMessage ? (
                            <Loader2 className="h-5 w-5 text-gray-600 mt-0.5 animate-spin" />
                          ) : (
                            <MessageSquare className="h-5 w-5 text-blood-red-600 mt-0.5" />
                          )}
                          <div className="flex-1">
                            <h3 className={`font-medium mb-1 ${
                              isSystemMessage ? 'text-blue-900' : 
                              isErrorMessage ? 'text-red-900' :
                              isLoadingMessage ? 'text-gray-700' : 'text-gray-900'
                            }`}>
                              {message.question}
                            </h3>
                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                              {!isSystemMessage && <span>Mode: {message.mode}</span>}
                              <span>{message.timestamp.toLocaleTimeString()}</span>
                              {!isSystemMessage && <span>{message.citations.length} sources</span>}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Answer */}
                      <div className={`rounded-md p-4 ${
                        isSystemMessage ? 'bg-blue-100' :
                        isErrorMessage ? 'bg-red-100' :
                        isLoadingMessage ? 'bg-gray-100' : 'bg-gray-50'
                      }`}>
                        <div className="prose prose-sm max-w-none">
                          <p className={`leading-relaxed whitespace-pre-line ${
                            isSystemMessage ? 'text-blue-800' :
                            isErrorMessage ? 'text-red-800' :
                            isLoadingMessage ? 'text-gray-600' : 'text-gray-700'
                          }`}>
                            {message.answer}
                          </p>
                        </div>
                      </div>

                      {/* Citations Summary */}
                      {message.citations.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <div className="flex items-center space-x-2 text-sm text-gray-600">
                            <FileText className="h-4 w-4" />
                            <span>
                              {message.citations.length} source{message.citations.length !== 1 ? 's' : ''}: 
                              {message.citations.slice(0, 2).map(c => c.title || c.doc_id).join(', ')}
                              {message.citations.length > 2 && `, +${message.citations.length - 2} more`}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Chat Input */}
          <ChatBox onSendMessage={handleSendMessage} isLoading={isLoading} />
        </div>

        {/* Sources Panel */}
        <SourcesPanel 
          citations={selectedCitations} 
          isVisible={selectedCitations.length > 0}
        />
      </div>

      {/* Disclaimer Footer */}
      <footer className="bg-yellow-50 border-t border-yellow-200 px-4 py-3">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center space-x-2 text-sm text-yellow-800">
            <AlertTriangle className="h-4 w-4 flex-shrink-0" />
            <p>
              <strong>Medical Disclaimer:</strong> This AI assistant provides information for reference only. 
              Always consult qualified medical professionals for medical decisions and follow official protocols.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ChatPage;
