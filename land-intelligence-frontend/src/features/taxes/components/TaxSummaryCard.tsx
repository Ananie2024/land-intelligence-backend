// Tax Summary Card Component
// Land Intelligence System

import { DollarSign, CheckCircle, Clock, AlertTriangle } from 'lucide-react';
import type { TaxSummary } from '@/types/tax';

interface TaxSummaryCardProps {
  summary: TaxSummary;
}

export const TaxSummaryCard: React.FC<TaxSummaryCardProps> = ({ summary }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="bg-slate-900/40 p-6 rounded-lg border border-slate-800">
        <div className="flex items-center">
          <div className="p-2 rounded-lg bg-primary-500/20">
            <DollarSign className="h-6 w-6 text-primary-400" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-slate-400">Total Tax Due</p>
            <p className="text-2xl font-bold text-white">
              RWF {summary.total_tax_amount.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-slate-900/40 p-6 rounded-lg border border-slate-800">
        <div className="flex items-center">
          <div className="p-2 rounded-lg bg-success/20">
            <CheckCircle className="h-6 w-6 text-success" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-slate-400">Paid</p>
            <p className="text-2xl font-bold text-white">
              RWF {summary.paid_amount.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-slate-900/40 p-6 rounded-lg border border-slate-800">
        <div className="flex items-center">
          <div className="p-2 rounded-lg bg-warning/20">
            <Clock className="h-6 w-6 text-warning" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-slate-400">Pending</p>
            <p className="text-2xl font-bold text-white">
              RWF {summary.pending_amount.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-slate-900/40 p-6 rounded-lg border border-slate-800">
        <div className="flex items-center">
          <div className="p-2 rounded-lg bg-red-500/20">
            <AlertTriangle className="h-6 w-6 text-red-400" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-slate-400">Overdue</p>
            <p className="text-2xl font-bold text-white">
              RWF {summary.overdue_amount.toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaxSummaryCard;
