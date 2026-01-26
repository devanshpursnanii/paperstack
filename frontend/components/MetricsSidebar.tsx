'use client';

import { Clock, FileText, Activity, ChevronDown, ChevronRight, Zap } from 'lucide-react';
import { useSession } from '@/contexts/SessionContext';
import { useState } from 'react';

export default function MetricsSidebar() {
  const { sessionInfo, messages, queryMetrics } = useSession();
  const [expandedQueryId, setExpandedQueryId] = useState<string | null>(null);

  const citations = messages
    .filter((m) => m.role === 'assistant' && m.citations)
    .flatMap((m) => m.citations || []);

  const uniquePapers = new Set(citations.map((c) => c.paper)).size;

  const formatTime = (ms: number) => {
    return ms >= 1000 ? `${(ms / 1000).toFixed(2)}s` : `${ms.toFixed(0)}ms`;
  };

  const formatTokens = (tokens: number) => {
    return tokens >= 1000 ? `${(tokens / 1000).toFixed(1)}k` : tokens.toString();
  };

  const truncateQuery = (query: string, maxLength = 40) => {
    return query.length > maxLength ? query.substring(0, maxLength) + '...' : query;
  };

  return (
    <div className="flex h-full flex-col rounded-xl shadow-lg bg-white border-2 border-gray-400">
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <h2 className="text-xl font-serif font-semibold text-gray-900 text-center">Session Activity</h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {!sessionInfo ? (
          <div className="flex h-full items-center justify-center text-center">
            <p className="text-sm text-gray-500">Loading session data...</p>
          </div>
        ) : (
          <>
            {/* Session ID */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-4 w-4 text-gray-500" />
                <span className="text-xs font-medium text-gray-700">Session</span>
              </div>
              <p className="text-xs font-mono text-gray-600 break-all">
                {sessionInfo.session_id}
              </p>
            </div>

            {/* Query Performance Metrics - Hybrid Accordion */}
            {queryMetrics && queryMetrics.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="h-4 w-4 text-blue-500" />
                  <span className="text-xs font-medium text-gray-700">
                    Query Performance ({queryMetrics.length})
                  </span>
                </div>
                <div className="space-y-2">
                  {queryMetrics.map((metric, index) => {
                    const isExpanded = expandedQueryId === metric.request_id;
                    const totalTokens = metric.prompt_tokens + metric.total_chunk_tokens + metric.completion_tokens;
                    
                    return (
                      <div key={metric.request_id} className="border border-gray-200 rounded-lg overflow-hidden">
                        {/* Compact Row - Always Visible */}
                        <button
                          onClick={() => setExpandedQueryId(isExpanded ? null : metric.request_id)}
                          className="w-full px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
                        >
                          <div className="flex items-start gap-2">
                            <div className="mt-0.5">
                              {isExpanded ? (
                                <ChevronDown className="h-3 w-3 text-gray-500" />
                              ) : (
                                <ChevronRight className="h-3 w-3 text-gray-500" />
                              )}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-xs font-semibold text-gray-900">Q{index + 1}</span>
                                <span className="text-xs text-blue-600 font-medium">
                                  {formatTime(metric.total_latency_ms)}
                                </span>
                                <span className="text-xs text-gray-500">
                                  {formatTokens(totalTokens)} tok
                                </span>
                              </div>
                              <p className="text-xs text-gray-600 truncate">
                                {truncateQuery(metric.query)}
                              </p>
                            </div>
                          </div>
                        </button>

                        {/* Expanded Details */}
                        {isExpanded && (
                          <div className="px-3 py-3 bg-white border-t border-gray-200 space-y-2">
                            <div>
                              <p className="text-xs font-medium text-gray-700 mb-1">Query</p>
                              <p className="text-xs text-gray-600 leading-relaxed">
                                {metric.query}
                              </p>
                            </div>
                            
                            <div className="grid grid-cols-2 gap-2 pt-2">
                              <div>
                                <p className="text-xs text-gray-500">Total Time</p>
                                <p className="text-sm font-semibold text-gray-900">
                                  {formatTime(metric.total_latency_ms)}
                                </p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500">LLM Time</p>
                                <p className="text-sm font-semibold text-gray-900">
                                  {formatTime(metric.llm_latency_ms)}
                                </p>
                              </div>
                            </div>

                            <div className="pt-2 border-t border-gray-100">
                              <p className="text-xs font-medium text-gray-700 mb-2">Token Breakdown</p>
                              <div className="space-y-1">
                                <div className="flex justify-between text-xs">
                                  <span className="text-gray-600">Prompt</span>
                                  <span className="font-mono text-gray-900">{metric.prompt_tokens.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between text-xs">
                                  <span className="text-gray-600">Context</span>
                                  <span className="font-mono text-gray-900">{metric.total_chunk_tokens.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between text-xs">
                                  <span className="text-gray-600">Completion</span>
                                  <span className="font-mono text-gray-900">{metric.completion_tokens.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between text-xs font-semibold pt-1 border-t border-gray-200">
                                  <span className="text-gray-700">Total</span>
                                  <span className="font-mono text-gray-900">{totalTokens.toLocaleString()}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Loaded Papers */}
            {sessionInfo.loaded_papers.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="text-xs font-medium text-gray-700">
                    Loaded Papers ({sessionInfo.loaded_papers.length})
                  </span>
                </div>
                <div className="space-y-1">
                  {sessionInfo.loaded_papers.map((paper, index) => (
                    <p key={index} className="text-xs text-gray-600 line-clamp-2">
                      {paper}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {/* Citations */}
            {citations.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="text-xs font-medium text-gray-700">Citations</span>
                </div>
                <div className="space-y-2">
                  <p className="text-sm text-gray-900">{uniquePapers} papers cited</p>
                  <p className="text-sm text-gray-900">{citations.length} total citations</p>
                </div>
              </div>
            )}

            {/* Activity */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span className="text-xs font-medium text-gray-700">Activity</span>
              </div>
              <div className="space-y-1 text-xs text-gray-600">
                <p>Brain searches: {sessionInfo.brain_searches_used}/3</p>
                <p>Chat messages: {sessionInfo.chat_messages_used}/5</p>
                <p>
                  Last active:{' '}
                  {new Date(sessionInfo.last_activity).toLocaleTimeString()}
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
