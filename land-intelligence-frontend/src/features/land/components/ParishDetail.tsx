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
      </div>
    </div>
  );
};

export default ParishDetail;