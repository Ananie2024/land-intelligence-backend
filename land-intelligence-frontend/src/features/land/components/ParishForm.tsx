// Parish Form Component
// Land Intelligence System

import { useForm } from 'react-hook-form';
import { FormField } from '@/components/ui/FormField';
import type { Parish, ParishCreate } from '@/types/land';

interface ParishFormProps {
  parish?: Parish | null;
  onSubmit: (data: ParishCreate) => Promise<void>;
  isLoading?: boolean;
}

export const ParishForm: React.FC<ParishFormProps> = ({ parish, onSubmit, isLoading = false }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ParishCreate>({
    defaultValues: parish ? {
      name: parish.name,
    } : undefined,
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <FormField
        label="Parish Name"
        name="name"
        type="text"
        register={register}
        validation={{ required: 'Name is required' }}
        error={errors.name}
        disabled={isLoading}
      />

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-500 disabled:opacity-50 transition-colors"
        >
          {isLoading ? 'Saving...' : parish ? 'Update Parish' : 'Create Parish'}
        </button>
      </div>
    </form>
  );
};

export default ParishForm;