import { ExternalLink } from 'lucide-react';
import type { Paper } from '@/types';

interface PaperCardProps {
  paper: Paper;
  isSelected: boolean;
  onToggle: () => void;
}

export default function PaperCard({ paper, isSelected, onToggle }: PaperCardProps) {
  return (
    <div
      className={`cursor-pointer rounded-lg border p-3 transition-all ${
        isSelected
          ? 'border-gray-900 bg-gray-100'
          : 'border-gray-200 bg-white hover:border-gray-300'
      }`}
      onClick={onToggle}
    >
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={onToggle}
          className="mt-1 h-4 w-4 rounded border-gray-300 text-gray-900 focus:ring-gray-900 accent-gray-900"
          onClick={(e) => e.stopPropagation()}
        />
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-gray-900 line-clamp-2 mb-1">
            {paper.title}
          </h3>
          <p className="text-xs text-gray-600 mb-2">{paper.authors}</p>
          <p className="text-xs text-gray-500 line-clamp-2 mb-2">{paper.abstract}</p>
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-900">
              Score: {paper.score.toFixed(3)}
            </span>
            <a
              href={paper.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
              onClick={(e) => e.stopPropagation()}
            >
              <ExternalLink className="h-3 w-3" />
              <span>arXiv</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
