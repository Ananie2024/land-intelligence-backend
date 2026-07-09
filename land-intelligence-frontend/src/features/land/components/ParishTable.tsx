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
      <div className="text-center py-12">
        <p className="text-gray-500">No parishes found</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Parish
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Code
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Parcels
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Contact
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {parishes.map((parish) => (
            <tr key={parish.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-gray-400 mr-2" />
                  <div>
                    <div className="text-sm font-medium text-gray-900">{parish.name}</div>
                    {parish.description && (
                      <div className="text-sm text-gray-500">{parish.description}</div>
                    )}
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {parish.code}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {parish.parcel_count}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {parish.contact_email && (
                  <div className="text-sm text-gray-900">{parish.contact_email}</div>
                )}
                {parish.contact_phone && (
                  <div className="text-sm text-gray-500">{parish.contact_phone}</div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div className="flex items-center justify-end gap-2">
                  <button
                    onClick={() => onView(parish)}
                    className="text-gray-400 hover:text-gray-600"
                    title="View"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onEdit(parish)}
                    className="text-indigo-600 hover:text-indigo-900"
                    title="Edit"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onDelete(parish)}
                    className="text-red-600 hover:text-red-900"
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