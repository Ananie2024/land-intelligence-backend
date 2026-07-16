// Parish Form Component
// Land Intelligence System

import { useForm } from 'react-hook-form';
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
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
          Parish Name
        </label>
        <input
          {...register('name', { required: 'Name is required' })}
          type="text"
          id="name"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
        )}
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {isLoading ? 'Saving...' : parish ? 'Update Parish' : 'Create Parish'}
        </button>
      </div>
    </form>
  );
};

export default ParishForm;