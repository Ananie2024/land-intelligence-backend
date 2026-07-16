// Parcel Table Component
// Land Intelligence System

import { Pencil, Trash2, Eye, MapPin } from 'lucide-react';
import type { Parcel } from '@/types/land';

interface ParcelTableProps {
  parcels: Parcel[];
  onEdit: (parcel: Parcel) => void;
  onDelete: (parcel: Parcel) => void;
  onView: (parcel: Parcel) => void;
}

export const ParcelTable: React.FC<ParcelTableProps> = ({ parcels, onEdit, onDelete, onView }) => {
  if (!parcels || parcels.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p>No parcels found</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-800">
        <thead className="bg-slate-900/60">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Parcel
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Parish
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Area (m²)
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Owner
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Deed Number
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-slate-900/40 divide-y divide-slate-800">
          {parcels.map((parcel) => (
            <tr key={parcel.id} className="hover:bg-slate-900/60 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-slate-400 mr-2" />
                  <span className="font-mono text-sm text-slate-200">{parcel.upi}</span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {parcel.parish_name || parcel.parish_id}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {parcel.area_sqm.toLocaleString()} m²
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">
                {parcel.owner_name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {parcel.title_deed_number || '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div className="flex items-center justify-end gap-2">
                   <button
                     onClick={() => onView(parcel)}
                     className="text-slate-400 hover:text-slate-200"
                     title="View"
                     aria-label={`View parcel ${parcel.upi}`}
                   >
                     <Eye className="h-4 w-4" />
                   </button>
                   <button
                     onClick={() => onEdit(parcel)}
                     className="text-primary-400 hover:text-primary-300"
                     title="Edit"
                     aria-label={`Edit parcel ${parcel.upi}`}
                   >
                     <Pencil className="h-4 w-4" />
                   </button>
                   <button
                     onClick={() => onDelete(parcel)}
                     className="text-red-400 hover:text-red-300"
                     title="Delete"
                     aria-label={`Delete parcel ${parcel.upi}`}
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

export default ParcelTable;
