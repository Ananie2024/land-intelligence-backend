// Parish Detail Component
// Land Intelligence System

import type { Parish } from '@/types/land';

interface ParishDetailProps {
  parish: Parish;
}

export const ParishDetail: React.FC<ParishDetailProps> = ({ parish }) => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">{parish.name}</h2>
        <p className="text-sm text-gray-500">Code: {parish.code}</p>
      </div>

      {parish.description && (
        <div>
          <h3 className="text-sm font-medium text-gray-700">Description</h3>
          <p className="mt-1 text-gray-900">{parish.description}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-medium text-gray-700">Contact Email</h3>
          <p className="mt-1 text-gray-900">{parish.contact_email || '-'}</p>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-700">Contact Phone</h3>
          <p className="mt-1 text-gray-900">{parish.contact_phone || '-'}</p>
        </div>
      </div>

      <div>
        <h3 className="text-sm font-medium text-gray-700">Parcels</h3>
        <p className="mt-1 text-gray-900">{parish.parcel_count}</p>
      </div>

      <div>
        <h3 className="text-sm font-medium text-gray-700">Registry Path</h3>
        <p className="mt-1 text-gray-900 font-mono text-sm">{parish.registry_path || '-'}</p>
      </div>
    </div>
  );
};

export default ParishDetail;