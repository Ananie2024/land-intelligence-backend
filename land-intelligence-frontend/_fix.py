import React from 'react';
import type { RegisterOptions, FieldError } from 'react-hook-form';

interface FormFieldProps {
  label: string;
  name: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'date' | 'file';
  register?: any; // react-hook-form's register function (optional for file inputs)
  validation?: RegisterOptions;
  error?: FieldError;
  disabled?: boolean;
  placeholder?: string;
  rows?: number;
  children?: React.ReactNode; // For select elements
  optional?: boolean;
  helperText?: string;
  required?: boolean;
  onChange?: (e: React.ChangeEvent<any>) => void;
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  name,
  type = 'text',
  register,
  validation,
  error,
  disabled,
  placeholder,
  rows,
  children,
  optional,
  helperText,
  required,
  onChange,
}) => {
  const inputClasses =
    'mt-1 block w-full rounded-lg border-slate-700 bg-slate-800/50 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-white placeholder-slate-500 disabled:opacity-50';
  const labelClasses = 'block text-sm font-medium text-slate-300';
  const errorClasses = 'mt-1 text-sm text-red-400';
  const helperClasses = 'mt-1 text-xs text-slate-500';

  const renderInput = () => {
    if (children) {
      // Select element
      return (
        <select
          {...register(name, validation)}
          id={name}
          className={inputClasses}
          disabled={disabled}
          onChange={onChange}
        >
          {children}
        </select>
      );
    }

    if (type === 'file') {
      return (
        <input
          type="file"
          id={name}
          className="mt-1 block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary-600 file:text-white hover:file:bg-primary-500 disabled:opacity-50"
          disabled={disabled}
          onChange={onChange}
          required={required}
        />
      );
    }

    if (rows) {
      // Textarea
      return (
        <textarea
          {...register(name, validation)}
          id={name}
          rows={rows}
          placeholder={placeholder}
          className={inputClasses}
          disabled={disabled}
          onChange={onChange}
        />
      );
    }

    // Standard input
    return (
      <input
        {...register(name, validation)}
        type={type}
        id={name}
        placeholder={placeholder}
        className={inputClasses}
        disabled={disabled}
        onChange={onChange}
        required={required}
      />
    );
  };

  return (
    <div>
      <label htmlFor={name} className={labelClasses}>
        {label}
        {required && !optional && <span className="text-red-400">*</span>}
        {optional && <span className="text-slate-500 ml-1">(optional)</span>}
      </label>
      {renderInput()}
      {error && <p className={errorClasses}>{error.message}</p>}
      {helperText && !error && <p className={helperClasses}>{helperText}</p>}
    </div>
  );
};