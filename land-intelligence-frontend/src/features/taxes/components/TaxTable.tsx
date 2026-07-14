// Tax Table Component
// Land Intelligence System

import { Eye, DollarSign } from 'lucide-react';
import type { TaxPayment } from '@/types/tax';
import type { TaxRecordSummary } from '@/services/reportService';

interface TaxTableProps {
  records: TaxRecordSummary[];
  onView: (record: TaxRecordSummary) => void;
}

export const TaxTable: React.FC<TaxTableProps> = ({ records, onView }) => {
  if (!records || records.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p>No tax records found</p>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'bg-success/20 text-success';
      case 'overdue':
        return 'bg-red-500/20 text-red-400';
      default:
        return 'bg-warning/20 text-warning';
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-800">
        <thead className="bg-slate-900/60">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Year
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Assessed Value
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Tax Amount
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Penalties
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Total Due
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Due Date
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-slate-900/40 divide-y divide-slate-800">
          {records.map((record) => (
            <tr key={record.id} className="hover:bg-slate-900/60 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">
                {record.assessment_year}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                RWF {record.assessed_value.toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                RWF {record.base_tax_amount.toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                RWF {record.penalties_amount.toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-200">
                RWF {record.total_amount.toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(record.status)}`}>
                  {record.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {new Date(record.due_date).toLocaleDateString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={() => onView(record)}
                  className="text-slate-400 hover:text-slate-200"
                  title="View"
                >
                  <Eye className="h-4 w-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TaxTable;
