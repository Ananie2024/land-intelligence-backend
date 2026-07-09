// Dashboard Statistics Types
export interface ParishStats {
  total_parishes: number;
  total_parcels: number;
  avg_parcels_per_parish: number;
}

export interface ParcelStats {
  total_parcels: number;
  total_area_sqm: number;
  total_valuation: number;
  parcels_with_deeds: number;
}

export interface UserStats {
  total_users: number;
  admin_count: number;
  client_count: number;
  viewer_count: number;
}

export interface DocumentStats {
  total_documents: number;
  total_size_bytes: number;
}

export interface DatabaseStats {
  database_status: string;
  database_version?: string | null;
}

export interface SystemStats {
  parishes: ParishStats;
  parcels: ParcelStats;
  users: UserStats;
  documents: DocumentStats;
  database: DatabaseStats;
}
