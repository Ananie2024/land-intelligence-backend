// Parcel Form Component
// Land Intelligence System

import { useForm } from 'react-hook-form';
import { FormField } from '@/components/ui/FormField';
import type { Parcel, ParcelCreate } from '@/types/land';

interface ParcelFormProps {
  parcel?: Parcel | null;
  onSubmit: (data: ParcelCreate) => Promise<void>;
  isLoading?: boolean;
  parishes?: Array<{ id: string; name: string }>;
}

export const ParcelForm: React.FC<ParcelFormProps> = ({ parcel, onSubmit, isLoading = false, parishes = [] }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ParcelCreate>({
    defaultValues: parcel ? {
      upi: parcel.upi,
      parish_id: parcel.parish_id,
      area_sqm: parcel.area_sqm,
      owner_name: parcel.owner_name,
      location_description: parcel.location_description || '',
      geometry_wkb: parcel.geometry_wkb || '',
    } : undefined,
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <FormField
        label="UPI (Unique Parcel Identifier)"
        name="upi"
        type="text"
        register={register}
        validation={{ required: 'UPI is required' }}
        error={errors.upi}
        disabled={isLoading}
        placeholder="e.g., 1/02/02/03/1390"
      />

      <FormField
        label="Parish"
        name="parish_id"
        register={register}
        validation={{ required: 'Parish is required' }}
        error={errors.parish_id}
        disabled={isLoading}
      >
        <option value="">Select a parish</option>
        {parishes.map((p) => (
          <option key={p.id} value={p.id}>{p.name}</option>
        ))}
      </FormField>

      <FormField
        label="Area (m²)"
        name="area_sqm"
        type="number"
        register={register}
        validation={{ required: 'Area is required', valueAsNumber: true }}
        error={errors.area_sqm}
        disabled={isLoading}
      />

      <FormField
        label="Owner Name"
        name="owner_name"
        type="text"
        register={register}
        validation={{ required: 'Owner name is required' }}
        error={errors.owner_name}
        disabled={isLoading}
      />

      <FormField
        label="Location Description"
        name="location_description"
        type="text"
        register={register}
        disabled={isLoading}
        optional
        rows={2}
      />

      <FormField
        label="Geometry (WKB)"
        name="geometry_wkb"
        type="text"
        register={register}
        disabled={isLoading}
        optional
        rows={2}
        helperText="Hex-encoded Well-Known Binary geometry (optional)"
      />

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-500 disabled:opacity-50 transition-colors"
        >
          {isLoading ? 'Saving...' : parcel ? 'Update Parcel' : 'Create Parcel'}
        </button>
      </div>
    </form>
  );
};

export default ParcelForm;