/**
 * Lease Agreement Types
 * Land Intelligence System
 */

export type LeaseStatus = 'draft' | 'active' | 'expired' | 'terminated' | 'renewed';
export type PaymentFrequency = 'monthly' | 'quarterly' | 'semi_annually' | 'annually';
export type LeasePaymentStatus = 'pending' | 'paid' | 'overdue' | 'partial' | 'cancelled';

export interface LeasePaymentSchedule {
  id: string;
  lease_id: string;
  due_date: string;
  amount_due: number;
  amount_paid: number;
  status: LeasePaymentStatus;
  paid_date?: string;
  payment_reference?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ParcelMini {
  id: string;
  upi: string;
  owner_name: string;
  location_description?: string;
}

export interface LeaseAgreement {
  id: string;
  parcel_id: string;
  lease_number: string;
  tenant_name: string;
  tenant_contact?: string;
  tenant_id_number?: string;
  start_date: string;
  end_date: string;
  annual_rent_amount: number;
  payment_frequency: PaymentFrequency;
  installment_amount: number;
  status: LeaseStatus;
  purpose_use?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  parcel?: ParcelMini;
  payment_schedules?: LeasePaymentSchedule[];
}

export interface LeaseAgreementCreate {
  parcel_id: string;
  lease_number?: string;
  tenant_name: string;
  tenant_contact?: string;
  tenant_id_number?: string;
  start_date: string;
  end_date: string;
  annual_rent_amount: number;
  payment_frequency: PaymentFrequency;
  purpose_use?: string;
  notes?: string;
  auto_generate_schedules?: boolean;
}

export interface LeaseAgreementUpdate {
  tenant_name?: string;
  tenant_contact?: string;
  tenant_id_number?: string;
  start_date?: string;
  end_date?: string;
  annual_rent_amount?: number;
  payment_frequency?: PaymentFrequency;
  status?: LeaseStatus;
  purpose_use?: string;
  notes?: string;
}

export interface LeasePaymentRecordRequest {
  amount_paid: number;
  paid_date?: string;
  payment_reference?: string;
  notes?: string;
}

export interface LeaseSummaryStats {
  total_leases: number;
  active_leases: number;
  expired_leases: number;
  draft_leases: number;
  total_annual_revenue: number;
  total_collected_revenue: number;
  total_pending_revenue: number;
  overdue_payments_count: number;
}
