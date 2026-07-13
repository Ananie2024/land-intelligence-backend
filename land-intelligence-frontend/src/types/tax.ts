// Tax Types
// Land Intelligence System

export interface TaxPayment {
  id: string;
  parcel_upi: string;
  assessment_year: string;
  assessed_value: number;
  base_tax_amount: number;
  penalties_amount: number;
  total_amount: number;
  status: 'paid' | 'pending' | 'overdue';
  due_date: string;
  paid_date?: string | null;
}

export interface TaxSummary {
  total_assessed_value: number;
  total_tax_amount: number;
  total_penalties: number;
  paid_amount: number;
  pending_amount: number;
  overdue_amount: number;
}