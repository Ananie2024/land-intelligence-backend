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
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center">
          <div className="p-2 rounded-lg bg-blue-100">
            <DollarSign className="h-6 w-6 text-blue-600" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-500">Total Tax Due</p>
            <p className="text-2xl font-bold text-gray-900">
              ${summary.total_tax_amount.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center">
          <div className="p-2 rounded-lg bg-green-100">
            <CheckCircle className="h-6 w-6 text-green-600" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-500">Paid</p>
            <p className="text-2xl font-bold text-gray-900">
              ${summary.paid_amount.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center">
          <div className="p-2 rounded-lg bg-yellow-100">
            <Clock className="h-6 w-6 text-yellow-600" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-500">Pending</p>
            <p className="text-2xl font-bold text-gray-900">
              ${summary.pending_amount.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center">
          <div className="p-2 rounded-lg bg-red-100">
            <AlertTriangle className="h-6 w-6 text-red-600" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-500">Overdue</p>
            <p className="text-2xl font-bold text-gray-900">
              ${summary.overdue_amount.toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaxSummaryCard;