'use client';

import { Clock, FileText, Activity } from 'lucide-react';
import { useSession } from '@/contexts/SessionContext';

export default function MetricsSidebar() {
  const { sessionInfo, messages } = useSession();

  const citations = messages
    .filter((m) => m.role === 'assistant' && m.citations)
    .flatMap((m) => m.citations || []);

  const uniquePapers = new Set(citations.map((c) => c.paper)).size;

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
