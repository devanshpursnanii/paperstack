import { Loader2, Check, AlertCircle } from 'lucide-react';
import type { ThinkingStep } from '@/types';

interface ThinkingStepsProps {
  steps: ThinkingStep[];
}

export default function ThinkingSteps({ steps }: ThinkingStepsProps) {
  if (steps.length === 0) return null;

  return (
    <div className="mb-4 rounded-lg border border-gray-200 bg-gray-50 p-3">
      <div className="space-y-2">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            {step.status === 'in_progress' && (
              <Loader2 className="h-4 w-4 animate-spin text-gray-900" />
            )}
            {step.status === 'complete' && (
              <Check className="h-4 w-4 text-green-600" />
            )}
            {step.status === 'error' && (
              <AlertCircle className="h-4 w-4 text-red-600" />
            )}
            <span className="font-medium text-gray-700">{step.step}:</span>
            {step.result && (
              <span className="text-gray-600">{step.result}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
