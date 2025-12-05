import { Citation } from '../types';
import { FileText, Star } from 'lucide-react';

interface SourcesPanelProps {
  citations: Citation[];
  isVisible: boolean;
}

const SourcesPanel = ({ citations, isVisible }: SourcesPanelProps) => {
  if (!isVisible) return null;

  const formatScore = (score: number): string => {
    return (score * 100).toFixed(1);
  };

  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600 bg-green-50';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-2">
          <FileText className="h-5 w-5 text-blood-red-600" />
          <h3 className="font-semibold text-gray-900">
            Sources ({citations.length})
          </h3>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          Documents used to generate the response
        </p>
      </div>

      {/* Citations List */}
      <div className="flex-1 overflow-y-auto">
        {citations.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <FileText className="h-12 w-12 mx-auto text-gray-300 mb-3" />
            <p className="text-sm">No sources found</p>
            <p className="text-xs mt-1">
              Try asking a question to see citations
            </p>
          </div>
        ) : (
          <div className="space-y-4 p-4">
            {citations.map((citation, index) => (
              <div
                key={`${citation.doc_id}-${citation.chunk_id || index}`}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                {/* Citation Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-gray-900 truncate">
                      {citation.title || citation.doc_id}
                    </h4>
                    <p className="text-xs text-gray-500 mt-1">
                      Document: {citation.doc_id}
                    </p>
                    {citation.chunk_id && (
                      <p className="text-xs text-gray-500">
                        Chunk: {citation.chunk_id}
                      </p>
                    )}
                  </div>
                  
                  {/* Relevance Score */}
                  <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getScoreColor(citation.score)}`}>
                    <Star className="h-3 w-3" />
                    <span>{formatScore(citation.score)}%</span>
                  </div>
                </div>

                {/* Citation Snippet */}
                <div className="bg-gray-50 rounded-md p-3">
                  <p className="text-sm text-gray-700 leading-relaxed">
                    "{citation.snippet}"
                  </p>
                </div>

                {/* Citation Footer */}
                <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                  <span>Citation [{index + 1}]</span>
                  <span>Relevance: {formatScore(citation.score)}%</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer with Info */}
      {citations.length > 0 && (
        <div className="p-3 border-t border-gray-200 bg-gray-50">
          <div className="text-xs text-gray-600">
            <div className="flex items-center justify-between">
              <span>Relevance Scores:</span>
              <div className="flex space-x-2">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>80%+</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span>60%+</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span>&lt;60%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SourcesPanel;
