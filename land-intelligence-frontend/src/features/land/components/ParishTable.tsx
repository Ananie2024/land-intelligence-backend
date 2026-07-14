// Parish Table Component
// Land Intelligence System

import { Pencil, Trash2, Eye, MapPin } from 'lucide-react';
import type { Parish } from '@/types/land';

interface ParishTableProps {
  parishes: Parish[];
  onEdit: (parish: Parish) => void;
  onDelete: (parish: Parish) => void;
  onView: (parish: Parish) => void;
}

export const ParishTable: React.FC<ParishTableProps> = ({ parishes, onEdit, onDelete, onView }) => {
  if (!parishes || parishes.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p>No parishes found</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-800">
        <thead className="bg-slate-900/60">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Parish
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Code
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Parcels
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Contact
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-slate-900/40 divide-y divide-slate-800">
          {parishes.map((parish) => (
            <tr key={parish.id} className="hover:bg-slate-900/60 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-slate-400 mr-2" />
                  <div>
                    <div className="text-sm font-medium text-slate-200">{parish.name}</div>
                    {parish.description && (
                      <div className="text-sm text-slate-400">{parish.description}</div>
                    )}
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {parish.code}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {parish.parcel_count}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {parish.contact_email && (
                  <div className="text-sm text-slate-200">{parish.contact_email}</div>
                )}
                {parish.contact_phone && (
                  <div className="text-sm text-slate-400">{parish.contact_phone}</div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div className="flex items-center justify-end gap-2">
                  <button
                    onClick={() => onView(parish)}
                    className="text-slate-400 hover:text-slate-200"
                    title="View"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onEdit(parish)}
                    className="text-primary-400 hover:text-primary-300"
                    title="Edit"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onDelete(parish)}
                    className="text-red-400 hover:text-red-300"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ParishTable;
