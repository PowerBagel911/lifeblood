import { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { ResponseMode } from '../types';
import ModeSelect from './ModeSelect';

interface ChatBoxProps {
  onSendMessage: (question: string, mode: ResponseMode) => void;
  isLoading?: boolean;
}

const ChatBox = ({ onSendMessage, isLoading = false }: ChatBoxProps) => {
  const [question, setQuestion] = useState('');
  const [mode, setMode] = useState<ResponseMode>('general');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() && !isLoading) {
      onSendMessage(question.trim(), mode);
      setQuestion('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="bg-white border-t border-gray-200 p-4">
      <div className="max-w-4xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Mode Selection */}
          <div className="flex justify-start">
            <div className="w-64">
              <ModeSelect
                mode={mode}
                onChange={setMode}
                disabled={isLoading}
              />
            </div>
          </div>

          {/* Input Area */}
          <div className="flex space-x-4 items-end">
            <div className="flex-1">
              <label htmlFor="question" className="sr-only">
                Ask a question about medical operations
              </label>
              <textarea
                id="question"
                rows={3}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                placeholder="Ask a question about blood donation procedures, eligibility requirements, safety protocols..."
                className="w-full px-4 py-3 text-sm border border-gray-300 rounded-lg 
                         resize-none focus:outline-none focus:ring-2 focus:ring-blood-red-500 
                         focus:border-blood-red-500 disabled:bg-gray-50 disabled:text-gray-500
                         placeholder-gray-500"
              />
              <div className="mt-2 text-xs text-gray-500">
                Press Enter to send, Shift+Enter for new line
              </div>
            </div>
            
            <button
              type="submit"
              disabled={!question.trim() || isLoading}
              className="px-6 py-3 bg-blood-red-600 text-white rounded-lg font-medium
                       hover:bg-blood-red-700 focus:outline-none focus:ring-2 
                       focus:ring-blood-red-500 focus:ring-offset-2
                       disabled:bg-gray-300 disabled:cursor-not-allowed
                       transition-colors duration-200 flex items-center space-x-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Asking...</span>
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  <span>Send</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatBox;
