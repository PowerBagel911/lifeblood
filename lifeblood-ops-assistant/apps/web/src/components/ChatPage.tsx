import { useState } from 'react';
import { Heart, MessageSquare, FileText, AlertTriangle } from 'lucide-react';
import { Message, ResponseMode, Citation } from '../types';
import ChatBox from './ChatBox';
import SourcesPanel from './SourcesPanel';

const ChatPage = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCitations, setSelectedCitations] = useState<Citation[]>([]);

  const handleSendMessage = async (question: string, mode: ResponseMode) => {
    setIsLoading(true);
    
    // TODO: Replace with actual API call
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Mock response
    const mockCitations: Citation[] = [
      {
        doc_id: 'donor_eligibility',
        title: 'Donor Eligibility Guidelines',
        chunk_id: 'donor_eligibility_chunk_0',
        snippet: 'Blood donors must be between 17-65 years old, weigh at least 110 pounds, and be in good health.',
        score: 0.89
      },
      {
        doc_id: 'safety_protocols',
        title: 'Safety Guidelines',
        chunk_id: 'safety_protocols_chunk_0', 
        snippet: 'All medical equipment must be sterilized before use. Staff must wear appropriate protective equipment.',
        score: 0.76
      }
    ];

    const mockMessage: Message = {
      id: Date.now().toString(),
      question,
      answer: mode === 'checklist' 
        ? "Based on the provided sources, here are the key donor eligibility requirements:\n\n1. Age: Must be between 17-65 years old [1]\n2. Weight: Must weigh at least 110 pounds [1]\n3. Health: Must be in good general health [1]\n4. Safety: All procedures follow strict safety protocols [2]"
        : "Based on the provided sources, blood donors must meet several eligibility requirements including being between 17-65 years old, weighing at least 110 pounds, and being in good health [1]. All procedures follow strict safety protocols to ensure donor and recipient safety [2].",
      citations: mockCitations,
      mode,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, mockMessage]);
    setSelectedCitations(mockCitations);
    setIsLoading(false);
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
            </div>
          </div>
        </div>
      </header>

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
                  
                  <div className="grid md:grid-cols-3 gap-4 max-w-3xl mx-auto">
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
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    onClick={() => handleMessageClick(message)}
                    className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 cursor-pointer hover:shadow-md transition-shadow"
                  >
                    {/* Question */}
                    <div className="mb-4">
                      <div className="flex items-start space-x-3">
                        <MessageSquare className="h-5 w-5 text-blood-red-600 mt-0.5" />
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900 mb-1">
                            {message.question}
                          </h3>
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span>Mode: {message.mode}</span>
                            <span>{message.timestamp.toLocaleTimeString()}</span>
                            <span>{message.citations.length} sources</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Answer */}
                    <div className="bg-gray-50 rounded-md p-4">
                      <div className="prose prose-sm max-w-none">
                        <p className="text-gray-700 leading-relaxed whitespace-pre-line">
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
                ))
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
