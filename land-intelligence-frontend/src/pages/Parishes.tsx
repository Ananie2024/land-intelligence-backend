import React, { useState, useEffect } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Building2 } from 'lucide-react';
import { landService } from '@/services/landService';
import type { Parish } from '@/types/land';
import { ParishTable } from '@/features/land/components/ParishTable';

export default function Parishes() {
  const [parishes, setParishes] = useState<Parish[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadParishes = async () => {
      try {
        const response = await landService.getParishes();
        if (response.success && response.data) {
          setParishes(response.data);
        }
      } catch (error) {
        console.error('Failed to load parishes', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadParishes();
  }, []);

  return (
    <PageContainer
      title="Parish Registries"
      subtitle="Parish administrative registry scopes within the Archdiocese of Kigali."
    >
      <div className="flex items-center gap-3 p-6 rounded-xl border border-slate-800/80 bg-slate-900/30 mb-6">
        <Building2 className="w-6 h-6 text-primary-400" />
        <div className="text-sm">
          <p className="text-white font-bold">Parish Scopes</p>
          <p className="text-slate-400 mt-1">Manage diocese parish assets and assign registry permissions to parish clients.</p>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-slate-400">Loading parishes...</div>
      ) : (
        <ParishTable 
          parishes={parishes}
          onView={(parish) => console.log('View parish:', parish)}
          onEdit={(parish) => console.log('Edit parish:', parish)}
          onDelete={(parish) => console.log('Delete parish:', parish)}
        />
      )}
    </PageContainer>
  );
}