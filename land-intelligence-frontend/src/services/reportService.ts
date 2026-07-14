import { api } from '@/api/axios';
import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { APIResponse } from '@/types/api';

// Report export types
export type ExportFormat = 'pdf' | 'excel';

export interface TaxReportSummary {
  parcel_upi: string;
  upi: string;
  total_outstanding: number;
  overdue_amount: number;
  upcoming_amount: number;
  records: TaxRecordSummary[];
}

export interface TaxRecordSummary {
  id: string;
  assessment_year: string;
  assessed_value: number;
  base_tax_amount: number;
  penalties_amount: number;
  total_amount: number;
  status: string;
  due_date: string;
}

export interface GisComplianceReport {
  intersects: boolean;
  intersection_area: number;
  percentage_overlap: number;
  zoning_code: string;
}

export const reportService = {
  // Export methods for reports (returns Blob for file download)
  exportTaxReport: async (parcelId: string, format: ExportFormat = 'pdf'): Promise<Blob> => {
    const response = await api.get(ENDPOINTS.REPORTS.TAX(parcelId), {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },

  exportParcelsReport: async (format: ExportFormat = 'pdf', parishId?: string): Promise<Blob> => {
    const response = await api.get(ENDPOINTS.REPORTS.PARCELS, {
      params: { format, ...(parishId ? { parish_id: parishId } : {}) },
      responseType: 'blob',
    });
    return response.data;
  },

  exportDashboardReport: async (format: ExportFormat = 'pdf'): Promise<Blob> => {
    const response = await api.get(ENDPOINTS.REPORTS.DASHBOARD, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },

  // Legacy methods for API data fetching (use apiClient for standard APIResponse)
  getTaxReport: async (parcelId: string): Promise<APIResponse<TaxReportSummary>> => {
    return apiClient.get<TaxReportSummary>(ENDPOINTS.TAX.OUTSTANDING(parcelId));
  },

  getTaxHistoryReport: async (
    parcelId: string, 
    params?: { skip?: number; limit?: number }
  ): Promise<APIResponse<TaxRecordSummary[]>> => {
    return apiClient.get<TaxRecordSummary[]>(ENDPOINTS.TAX.HISTORY(parcelId), { params });
  },

  getGisOverlayReport: async (
    parcelUpi: string,
    zoningWkt: string,
    zoningCode: string
  ): Promise<APIResponse<GisComplianceReport>> => {
    return apiClient.post<GisComplianceReport>(ENDPOINTS.GIS.CHECK_OVERLAY, {
      parcel_upi: parcelUpi,
      zoning_wkt: zoningWkt,
      zoning_code: zoningCode,
    });
  },

  calculateDistance: async (payload: {
    geom1_wkt?: string;
    parcel_upi_1?: string;
    geom2_wkt?: string;
    parcel_upi_2?: string;
  }): Promise<APIResponse<{ distance_meters: number; message: string }>> => {
    return apiClient.post<{ distance_meters: number; message: string }>(ENDPOINTS.GIS.DISTANCE, payload);
  },

  // Additional GIS methods
  checkIntersection: async (payload: {
    geom1_wkt?: string;
    parcel_upi_1?: string;
    geom2_wkt?: string;
    parcel_upi_2?: string;
  }): Promise<APIResponse<{
    intersects: boolean;
    overlaps: boolean;
    intersection_area_sqm: number;
    percentage_overlap_geom1: number;
    percentage_overlap_geom2: number;
  }>> => {
    return apiClient.post(ENDPOINTS.GIS.INTERSECTS, payload);
  },

  containsPoint: async (payload: {
    geom_wkt?: string;
    parcel_upi?: string;
    x: number;
    y: number;
  }): Promise<APIResponse<{ contains: boolean; intersects: boolean }>> => {
    return apiClient.post(ENDPOINTS.GIS.CONTAINS_POINT, payload);
  },
};

export default reportService;
