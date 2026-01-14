'use client';

import { useState, useEffect } from 'react';
import { Search, Download, Loader2, Clock, CheckCircle } from 'lucide-react';
import { useSession } from '@/contexts/SessionContext';
import PaperCard from './PaperCard';

export default function BrainSidebar() {
  const {
    sessionInfo,
    papers,
    selectedPaperIds,
    loading,
    searchPapers,
    loadPapers,
    togglePaperSelection,
    clearPapers,
  } = useSession();

  const [searchQuery, setSearchQuery] = useState('');
  const [searchMode, setSearchMode] = useState<'title' | 'topic'>('topic');
  const [showSuccess, setShowSuccess] = useState(false);

  const brainQuota = sessionInfo?.quota_status.brain;
  const isDisabled = brainQuota && !brainQuota.allowed;

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim() || loading || isDisabled) return;
    await searchPapers(searchQuery, searchMode);
  };

  const handleLoad = async () => {
    if (selectedPaperIds.length === 0 || loading) return;
    const result = await loadPapers();
    if (result) {
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 4000);
    }
  };

  return (
    <div className="flex h-full flex-col rounded-xl shadow-lg bg-white border-2 border-gray-400 relative">
      {/* Success Popup */}
      {showSuccess && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-20 animate-slide-in">
          <div className="rounded-lg border-2 border-gray-900 bg-white px-4 py-2 shadow-xl">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-gray-900" />
              <p className="text-sm font-medium text-gray-900">
                Papers loaded! Proceed to PaperChat
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex flex-col items-center gap-1 flex-1">
            <h2 className="text-xl font-serif font-semibold text-gray-900">PaperBrain</h2>
            <span className="text-sm text-gray-500">
              {brainQuota ? `${brainQuota.searches_remaining}/${brainQuota.searches_used + brainQuota.searches_remaining}` : '3/3'} searches left
            </span>
          </div>
          {papers.length > 0 && (
            <button
              onClick={() => {
                if (confirm('Clear all search results?')) {
                  clearPapers();
                  setSearchQuery('');
                }
              }}
              className="px-3 py-1.5 text-xs font-medium text-gray-700 hover:text-gray-900 border-2 border-gray-300 hover:border-gray-400 rounded-lg transition-all"
              title="Clear search results"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Cooldown Overlay */}
      {isDisabled && brainQuota && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="rounded-lg bg-white p-6 shadow-lg">
            <div className="flex items-center gap-3">
              <Clock className="h-5 w-5 text-gray-900 animate-pulse" />
              <div>
                <p className="font-medium text-gray-900">Cooldown Active</p>
                <p className="text-sm text-gray-600">
                  Available in {brainQuota.cooldown_minutes} minutes
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search Form */}
      <div className="p-4">
        <form onSubmit={handleSearch} className="space-y-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search papers on arXiv..."
            disabled={loading || isDisabled}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900 disabled:bg-gray-100"
          />
          <select
            value={searchMode}
            onChange={(e) => setSearchMode(e.target.value as 'title' | 'topic')}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-gray-900 focus:outline-none focus:ring-1 focus:ring-gray-900 disabled:bg-gray-100"
            disabled={loading || isDisabled}
          >
            <option value="topic">Search by Topic (all fields)</option>
            <option value="title">Search by Title (exact match)</option>
          </select>
          <button
            type="submit"
            disabled={loading || isDisabled || !searchQuery.trim()}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
            Search Papers
          </button>
        </form>
      </div>

      {/* Papers List */}
      <div className="flex-1 overflow-y-auto p-4">
        {papers.length > 0 ? (
          <div className="space-y-3">
            {papers.map((paper) => (
              <PaperCard
                key={paper.arxiv_id}
                paper={paper}
                isSelected={selectedPaperIds.includes(paper.arxiv_id)}
                onToggle={() => togglePaperSelection(paper.arxiv_id)}
              />
            ))}
          </div>
        ) : (
          <div className="flex h-full items-center justify-center text-center">
            <p className="text-sm text-gray-500">
              Search for papers to get started
            </p>
          </div>
        )}
      </div>

      {/* Load Button */}
      {papers.length > 0 && (
        <div className="border-t border-gray-200 p-4">
          <button
            onClick={handleLoad}
            disabled={selectedPaperIds.length === 0 || loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Download className="h-4 w-4" />
            )}
            Load Selected Papers ({selectedPaperIds.length})
          </button>
        </div>
      )}
    </div>
  );
}
