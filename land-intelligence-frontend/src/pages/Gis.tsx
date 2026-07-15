// GIS Map Page — Spatial Analysis Tools
// Land Intelligence System

import React, { useState, useEffect, useCallback } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { GISMap, type ParcelGeoData, type MapSelectionMode } from '@/components/ui/GISMap';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { RefreshCw, Layers, MapPin, User, Ruler, DollarSign, FileText, Calendar, Crosshair, Route, Shrink, Expand, Pointer, Search, X } from 'lucide-react';
import { landService } from '@/services/landService';
import { reportService } from '@/services/reportService';
import type { Parcel } from '@/types/land';
import { toast } from 'react-hot-toast';

import { parseWkbToCoordinates } from '@/utils/wkbParser';

// ── Analysis result types ──────────────────────────────────────────────────
interface DistanceResult {
  distance_meters: number;
  message: string;
}

interface IntersectionResult {
  intersects: boolean;
  overlaps: boolean;
  intersection_area_sqm: number;
  percentage_overlap_geom1: number;
  percentage_overlap_geom2: number;
}

interface ContainsPointResult {
  contains: boolean;
  intersects: boolean;
}

interface OverlayResult {
  intersects: boolean;
  intersection_area: number;
  percentage_overlap: number;
  zoning_code: string;
}

type ActiveTool = 'distance' | 'intersects' | 'contains-point' | 'overlay' | null;

// ── Helper to format numbers ───────────────────────────────────────────────
const formatNumber = (value: number | undefined | null) => {
  if (value === null || value === undefined) return 'N/A';
  return new Intl.NumberFormat('rw-RW', { maximumFractionDigits: 2 }).format(value);
};

const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

// ── Main page component ────────────────────────────────────────────────────
export default function GisPage() {
  // Parcel data
  const [parcels, setParcels] = useState<ParcelGeoData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedParcel, setSelectedParcel] = useState<ParcelGeoData | null>(null);

  // Active analysis tool
  const [activeTool, setActiveTool] = useState<ActiveTool>(null);

  // Selection state – used by distance, intersects, overlay tools
  const [selectedParcelIds, setSelectedParcelIds] = useState<string[]>([]);
  const [selectionStep, setSelectionStep] = useState<1 | 2>(1);
  const [selectionMode, setSelectionMode] = useState<MapSelectionMode>('none');

  // Point mode – used by contains-point tool
  const [clickedPoint, setClickedPoint] = useState<[number, number] | null>(null);
  const [selectedPointParcel, setSelectedPointParcel] = useState<ParcelGeoData | null>(null);

  // Zoning overlay inputs
  const [zoningCode, setZoningCode] = useState('');
  const [zoningWkt, setZoningWkt] = useState('');

  // Results
  const [distanceResult, setDistanceResult] = useState<DistanceResult | null>(null);
  const [intersectionResult, setIntersectionResult] = useState<IntersectionResult | null>(null);
  const [containsPointResult, setContainsPointResult] = useState<ContainsPointResult | null>(null);
  const [overlayResult, setOverlayResult] = useState<OverlayResult | null>(null);

  // Loading per‑action
  const [actionLoading, setActionLoading] = useState(false);

  // ── Load parcels ──────────────────────────────────────────────────────────
  const loadParcels = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await landService.getParcelsForMap();
      if (response.success && response.data) {
        const geoParcels: ParcelGeoData[] = response.data.map((parcel: Parcel) => ({
          id: parcel.id,
          upi: parcel.upi,
          owner_name: parcel.owner_name,
          area_sqm: parcel.area_sqm,
          valuation: parcel.valuation ?? undefined,
          geometry: parseWkbToCoordinates(parcel.geometry_wkb),
        }));
        setParcels(geoParcels);
      } else {
        toast.error('Failed to load parcels for map');
      }
    } catch (error) {
      console.error('Failed to load parcels', error);
      toast.error('Failed to load parcels');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadParcels();
  }, [loadParcels]);

  // ── Tool activation helpers ──────────────────────────────────────────────
  const activateTool = useCallback((tool: ActiveTool) => {
    // Reset previous tool state
    setActiveTool(tool);
    setSelectedParcelIds([]);
    setSelectionStep(1);
    setClickedPoint(null);
    setSelectedPointParcel(null);
    setDistanceResult(null);
    setIntersectionResult(null);
    setContainsPointResult(null);
    setOverlayResult(null);
    setZoningCode('');
    setZoningWkt('');

    if (tool === 'distance' || tool === 'intersects') {
      setSelectionMode('select');
    } else if (tool === 'contains-point') {
      setSelectionMode('point');
    } else if (tool === 'overlay') {
      setSelectionMode('select');
    } else {
      setSelectionMode('none');
    }
  }, []);

  const deactivateTool = useCallback(() => {
    setActiveTool(null);
    setSelectionMode('none');
    setSelectedParcelIds([]);
    setSelectionStep(1);
    setClickedPoint(null);
    setSelectedPointParcel(null);
    setDistanceResult(null);
    setIntersectionResult(null);
    setContainsPointResult(null);
    setOverlayResult(null);
  }, []);

  // ── Parcel selection handler (select mode) ───────────────────────────────
  const handleParcelSelect = useCallback((parcel: ParcelGeoData) => {
    if (activeTool === 'overlay') {
      // Overlay only needs 1 parcel; clicking toggles selection
      if (selectedParcelIds.includes(parcel.id)) {
        setSelectedParcelIds([]);
      } else {
        setSelectedParcelIds([parcel.id]);
      }
      return;
    }

    // Distance & Intersects need 2 parcels (step 1 / step 2)
    if (selectionStep === 1) {
      setSelectedParcelIds([parcel.id]);
      setSelectionStep(2);
    } else {
      setSelectedParcelIds(prev => {
        // If same parcel clicked twice, reset to first
        if (prev[0] === parcel.id) {
          setSelectionStep(1);
          return [];
        }
        return [prev[0], parcel.id];
      });
      setSelectionStep(1); // reset after both selected
    }
  }, [activeTool, selectionStep, selectedParcelIds]);

  // ── Map click handler (point mode) ────────────────────────────────────────
  const handleMapClick = useCallback((latlng: [number, number]) => {
    setClickedPoint(latlng);

    // Find which parcel (if any) contains the clicked point
    const point = { lat: latlng[0], lng: latlng[1] };
    const containingParcel = parcels.find(p =>
      p.geometry.some(ring => {
        // Ray‑casting algorithm for point‑in‑polygon
        let inside = false;
        for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
          const xi = ring[i][1], yi = ring[i][0];
          const xj = ring[j][1], yj = ring[j][0];
          if ((yi > point.lat) !== (yj > point.lat) &&
              point.lng < ((xj - xi) * (point.lat - yi)) / (yj - yi) + xi) {
            inside = !inside;
          }
        }
        return inside;
      })
    );
    setSelectedPointParcel(containingParcel ?? null);
  }, [parcels]);

  // ── Distance calculation ──────────────────────────────────────────────────
  const handleCalculateDistance = useCallback(async () => {
    if (selectedParcelIds.length < 2) {
      toast.error('Please select two parcels');
      return;
    }
    const p1 = parcels.find(p => p.id === selectedParcelIds[0]);
    const p2 = parcels.find(p => p.id === selectedParcelIds[1]);
    if (!p1 || !p2) {
      toast.error('Selected parcels not found');
      return;
    }

    setActionLoading(true);
    try {
      const resp = await reportService.calculateDistance({
        parcel_upi_1: p1.upi,
        parcel_upi_2: p2.upi,
      });
      if (resp.success && resp.data) {
        setDistanceResult(resp.data);
        toast.success('Distance calculated');
      } else {
        toast.error(resp.message || 'Failed to calculate distance');
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to calculate distance');
    } finally {
      setActionLoading(false);
    }
  }, [selectedParcelIds, parcels]);

  // ── Intersection check ────────────────────────────────────────────────────
  const handleCheckIntersection = useCallback(async () => {
    if (selectedParcelIds.length < 2) {
      toast.error('Please select two parcels');
      return;
    }
    const p1 = parcels.find(p => p.id === selectedParcelIds[0]);
    const p2 = parcels.find(p => p.id === selectedParcelIds[1]);
    if (!p1 || !p2) {
      toast.error('Selected parcels not found');
      return;
    }

    setActionLoading(true);
    try {
      const resp = await reportService.checkIntersection({
        parcel_upi_1: p1.upi,
        parcel_upi_2: p2.upi,
      });
      if (resp.success && resp.data) {
        setIntersectionResult(resp.data as unknown as IntersectionResult);
        toast.success('Intersection check complete');
      } else {
        toast.error(resp.message || 'Failed to check intersection');
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to check intersection');
    } finally {
      setActionLoading(false);
    }
  }, [selectedParcelIds, parcels]);

  // ── Contains‑point check ──────────────────────────────────────────────────
  const handleCheckContainsPoint = useCallback(async () => {
    if (!clickedPoint) {
      toast.error('Please click a location on the map');
      return;
    }
    setActionLoading(true);
    try {
      const payload: { x: number; y: number; parcel_upi?: string } = {
        x: clickedPoint[1], // lng → x
        y: clickedPoint[0], // lat → y
      };
      if (selectedPointParcel) {
        payload.parcel_upi = selectedPointParcel.upi;
      }
      const resp = await reportService.containsPoint(payload);
      if (resp.success && resp.data) {
        setContainsPointResult(resp.data);
        toast.success('Point containment check complete');
      } else {
        toast.error(resp.message || 'Failed to check point containment');
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to check point containment');
    } finally {
      setActionLoading(false);
    }
  }, [clickedPoint, selectedPointParcel]);

  // ── Zoning overlay check ──────────────────────────────────────────────────
  const handleCheckOverlay = useCallback(async () => {
    if (selectedParcelIds.length === 0) {
      toast.error('Please select a parcel');
      return;
    }
    if (!zoningCode.trim()) {
      toast.error('Please enter a zoning code');
      return;
    }
    if (!zoningWkt.trim()) {
      toast.error('Please enter the zoning district WKT geometry');
      return;
    }
    const p = parcels.find(p => p.id === selectedParcelIds[0]);
    if (!p) {
      toast.error('Selected parcel not found');
      return;
    }

    setActionLoading(true);
    try {
      const resp = await reportService.getGisOverlayReport(p.upi, zoningWkt.trim(), zoningCode.trim());
      if (resp.success && resp.data) {
        setOverlayResult(resp.data);
        toast.success('Zoning overlay check complete');
      } else {
        toast.error(resp.message || 'Failed to check zoning overlay');
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to check zoning overlay');
    } finally {
      setActionLoading(false);
    }
  }, [selectedParcelIds, zoningCode, zoningWkt, parcels]);

  // ── Parcel detail modal ───────────────────────────────────────────────────
  const handleParcelClick = (parcel: ParcelGeoData) => {
    // In normal (non‑tool) mode open the detail modal
    if (!activeTool) {
      setSelectedParcel(parcel);
    }
  };

  const closeModal = () => setSelectedParcel(null);

  // ── Derive selected parcel objects for display ───────────────────────────
  const selectedParcels = selectedParcelIds.map(id => parcels.find(p => p.id === id)).filter(Boolean) as ParcelGeoData[];

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <PageContainer
      title="GIS Map View"
      subtitle="Interactive map of land parcels with spatial analysis tools."
      action={
        <Button
          variant="secondary"
          leftIcon={<RefreshCw className="w-4 h-4" />}
          onClick={loadParcels}
          disabled={isLoading}
        >
          Refresh Map
        </Button>
      }
    >
      <div className="space-y-4">
        {/* ── Toolbar ────────────────────────────────────────────────── */}
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Crosshair className="w-5 h-5" />
                  Spatial Analysis Tools
                </CardTitle>
                <CardDescription>
                  Select a tool below to run GIS analysis on parcels.
                </CardDescription>
              </div>
              {activeTool && (
                <Button variant="ghost" size="sm" onClick={deactivateTool} leftIcon={<X className="w-4 h-4" />}>
                  Cancel Tool
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Button
                variant={activeTool === 'distance' ? 'primary' : 'secondary'}
                size="sm"
                leftIcon={<Route className="w-4 h-4" />}
                onClick={() => activateTool('distance')}
              >
                Measure Distance
              </Button>
              <Button
                variant={activeTool === 'intersects' ? 'primary' : 'secondary'}
                size="sm"
                leftIcon={<Shrink className="w-4 h-4" />}
                onClick={() => activateTool('intersects')}
              >
                Check Intersection
              </Button>
              <Button
                variant={activeTool === 'contains-point' ? 'primary' : 'secondary'}
                size="sm"
                leftIcon={<Pointer className="w-4 h-4" />}
                onClick={() => activateTool('contains-point')}
              >
                Contains Point
              </Button>
              <Button
                variant={activeTool === 'overlay' ? 'primary' : 'secondary'}
                size="sm"
                leftIcon={<Layers className="w-4 h-4" />}
                onClick={() => activateTool('overlay')}
              >
                Zoning Overlay
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* ── Active tool panel ──────────────────────────────────────── */}
        {activeTool && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-base">
                {activeTool === 'distance' && <><Route className="w-4 h-4" /> Measure Distance</>}
                {activeTool === 'intersects' && <><Shrink className="w-4 h-4" /> Check Intersection</>}
                {activeTool === 'contains-point' && <><Pointer className="w-4 h-4" /> Contains Point</>}
                {activeTool === 'overlay' && <><Layers className="w-4 h-4" /> Zoning Overlay Compliance</>}
              </CardTitle>
              <CardDescription>
                {activeTool === 'distance' && 'Click two parcels on the map (1st → 2nd) to measure the distance between them.'}
                {activeTool === 'intersects' && 'Click two parcels on the map (1st → 2nd) to check their intersection.'}
                {activeTool === 'contains-point' && 'Click any location on the map to check if it falls within a parcel.'}
                {activeTool === 'overlay' && 'Select a parcel, then enter the zoning district geometry & code to check compliance.'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* ── Distance ──────────────────────────────────────────── */}
              {activeTool === 'distance' && (
                <div className="space-y-3">
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-violet-500" />
                      <span className="text-slate-300">
                        Parcel 1: {selectedParcels[0] ? `${selectedParcels[0].upi} (${selectedParcels[0].owner_name})` : '— click map'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-violet-500" />
                      <span className="text-slate-300">
                        Parcel 2: {selectedParcels[1] ? `${selectedParcels[1].upi} (${selectedParcels[1].owner_name})` : '— click map'}
                      </span>
                    </div>
                  </div>
                  <Button
                    onClick={handleCalculateDistance}
                    disabled={selectedParcelIds.length < 2 || actionLoading}
                    leftIcon={<Ruler className="w-4 h-4" />}
                  >
                    {actionLoading ? 'Calculating…' : 'Calculate Distance'}
                  </Button>

                  {distanceResult && (
                    <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 space-y-1 mt-2">
                      <p className="text-lg font-semibold text-white">
                        {formatNumber(distanceResult.distance_meters)} <span className="text-sm font-normal text-slate-400">meters</span>
                      </p>
                      <p className="text-sm text-slate-400">{distanceResult.message}</p>
                    </div>
                  )}
                </div>
              )}

              {/* ── Intersection ────────────────────────────────────────── */}
              {activeTool === 'intersects' && (
                <div className="space-y-3">
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-violet-500" />
                      <span className="text-slate-300">
                        Parcel 1: {selectedParcels[0] ? `${selectedParcels[0].upi} (${selectedParcels[0].owner_name})` : '— click map'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-violet-500" />
                      <span className="text-slate-300">
                        Parcel 2: {selectedParcels[1] ? `${selectedParcels[1].upi} (${selectedParcels[1].owner_name})` : '— click map'}
                      </span>
                    </div>
                  </div>
                  <Button
                    onClick={handleCheckIntersection}
                    disabled={selectedParcelIds.length < 2 || actionLoading}
                    leftIcon={<Search className="w-4 h-4" />}
                  >
                    {actionLoading ? 'Checking…' : 'Check Intersection'}
                  </Button>

                  {intersectionResult && (
                    <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 space-y-1 mt-2">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${intersectionResult.intersects ? 'bg-green-500' : 'bg-red-500'}`} />
                        <span className="text-sm text-white">
                          Intersects: <strong>{intersectionResult.intersects ? 'Yes' : 'No'}</strong>
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${intersectionResult.overlaps ? 'bg-yellow-500' : 'bg-slate-500'}`} />
                        <span className="text-sm text-white">
                          Overlaps: <strong>{intersectionResult.overlaps ? 'Yes' : 'No'}</strong>
                        </span>
                      </div>
                      <p className="text-sm text-slate-300">
                        Intersection area: <strong>{formatNumber(intersectionResult.intersection_area_sqm)} sqm</strong>
                      </p>
                      <p className="text-sm text-slate-300">
                        Overlap of parcel 1: {formatNumber(intersectionResult.percentage_overlap_geom1)}%
                      </p>
                      <p className="text-sm text-slate-300">
                        Overlap of parcel 2: {formatNumber(intersectionResult.percentage_overlap_geom2)}%
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* ── Contains Point ───────────────────────────────────────── */}
              {activeTool === 'contains-point' && (
                <div className="space-y-3">
                  <div className="text-sm text-slate-300">
                    {clickedPoint ? (
                      <p>
                        Clicked location: <strong>{clickedPoint[0].toFixed(6)}, {clickedPoint[1].toFixed(6)}</strong>
                      </p>
                    ) : (
                      <p className="text-slate-400">Click on the map to select a point.</p>
                    )}
                    {selectedPointParcel && (
                      <p className="mt-1">
                        Nearest parcel: <strong>{selectedPointParcel.upi}</strong> ({selectedPointParcel.owner_name})
                      </p>
                    )}
                  </div>
                  <Button
                    onClick={handleCheckContainsPoint}
                    disabled={!clickedPoint || actionLoading}
                    leftIcon={<Search className="w-4 h-4" />}
                  >
                    {actionLoading ? 'Checking…' : 'Check Point Containment'}
                  </Button>

                  {containsPointResult && (
                    <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 space-y-1 mt-2">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${containsPointResult.contains ? 'bg-green-500' : 'bg-red-500'}`} />
                        <span className="text-sm text-white">
                          Contained in parcel: <strong>{containsPointResult.contains ? 'Yes' : 'No'}</strong>
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${containsPointResult.intersects ? 'bg-yellow-500' : 'bg-slate-500'}`} />
                        <span className="text-sm text-white">
                          Intersects parcel boundary: <strong>{containsPointResult.intersects ? 'Yes' : 'No'}</strong>
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* ── Zoning Overlay ────────────────────────────────────────── */}
              {activeTool === 'overlay' && (
                <div className="space-y-3">
                  <div className="text-sm text-slate-300">
                    Selected parcel:{' '}
                    {selectedParcels[0] ? (
                      <strong>{selectedParcels[0].upi} ({selectedParcels[0].owner_name})</strong>
                    ) : (
                      <span className="text-slate-400">— click a parcel on the map</span>
                    )}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">Zoning Code</label>
                      <input
                        type="text"
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-accent-500/50"
                        placeholder="e.g. R-1, C-2"
                        value={zoningCode}
                        onChange={e => setZoningCode(e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">Zoning District WKT</label>
                      <input
                        type="text"
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-accent-500/50"
                        placeholder="POLYGON((…))"
                        value={zoningWkt}
                        onChange={e => setZoningWkt(e.target.value)}
                      />
                    </div>
                  </div>
                  <Button
                    onClick={handleCheckOverlay}
                    disabled={selectedParcelIds.length === 0 || !zoningCode.trim() || !zoningWkt.trim() || actionLoading}
                    leftIcon={<Layers className="w-4 h-4" />}
                  >
                    {actionLoading ? 'Checking…' : 'Check Overlay Compliance'}
                  </Button>

                  {overlayResult && (
                    <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 space-y-1 mt-2">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${overlayResult.intersects ? 'bg-green-500' : 'bg-red-500'}`} />
                        <span className="text-sm text-white">
                          Intersects zoning district: <strong>{overlayResult.intersects ? 'Yes' : 'No'}</strong>
                        </span>
                      </div>
                      <p className="text-sm text-slate-300">
                        Zoning code: <strong>{overlayResult.zoning_code}</strong>
                      </p>
                      <p className="text-sm text-slate-300">
                        Intersection area: <strong>{formatNumber(overlayResult.intersection_area)} sqm</strong>
                      </p>
                      <p className="text-sm text-slate-300">
                        Percentage overlap: <strong>{formatNumber(overlayResult.percentage_overlap)}%</strong>
                      </p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* ── Active tool instruction banner ────────────────────────── */}
        {activeTool && (
          <div className={`px-4 py-2 rounded-lg text-sm flex items-center gap-2 ${
            activeTool === 'distance' || activeTool === 'intersects'
              ? 'bg-violet-500/10 border border-violet-500/30 text-violet-300'
              : activeTool === 'contains-point'
              ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300'
              : 'bg-amber-500/10 border border-amber-500/30 text-amber-300'
          }`}>
            {activeTool === 'distance' && <Route className="w-4 h-4 shrink-0" />}
            {activeTool === 'intersects' && <Shrink className="w-4 h-4 shrink-0" />}
            {activeTool === 'contains-point' && <Pointer className="w-4 h-4 shrink-0" />}
            {activeTool === 'overlay' && <Layers className="w-4 h-4 shrink-0" />}
            <span>
              {activeTool === 'distance' && 'Select mode active — click Parcel 1, then Parcel 2 on the map.'}
              {activeTool === 'intersects' && 'Select mode active — click Parcel 1, then Parcel 2 on the map.'}
              {activeTool === 'contains-point' && 'Point mode active — click any location on the map to test containment.'}
              {activeTool === 'overlay' && 'Select mode active — click a parcel on the map, then fill in the zoning details below.'}
            </span>
          </div>
        )}

        {/* ── Map ────────────────────────────────────────────────────── */}
        <Card>
          <CardHeader>
            <CardTitle>Parcel Map</CardTitle>
            <CardDescription>
              {activeTool
                ? 'Use the map to select parcels or points for spatial analysis.'
                : 'Click on a parcel to view details. Color-coded by valuation tiers.'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 mb-3 text-xs">
              <Layers className="w-4 h-4 text-slate-400" />
              <span className="text-slate-400">
                Legend:
                <span className="ml-2 px-2 py-0.5 rounded bg-slate-500/20">No valuation</span>
                <span className="ml-2 px-2 py-0.5 rounded bg-success/20">{'<'} 1M RWF</span>
                <span className="ml-2 px-2 py-0.5 rounded bg-warning/20">1M-5M RWF</span>
                <span className="ml-2 px-2 py-0.5 rounded bg-accent-500/20">{'>'} 5M RWF</span>
                {activeTool && (
                  <span className="ml-2 px-2 py-0.5 rounded bg-violet-500/40">Selected</span>
                )}
              </span>
            </div>
            <GISMap
              parcels={parcels}
              height="600px"
              onParcelClick={handleParcelClick}
              selectedParcelIds={selectedParcelIds}
              onParcelSelect={handleParcelSelect}
              onMapClick={handleMapClick}
              selectionMode={selectionMode}
              clickedPoint={clickedPoint}
            />
          </CardContent>
        </Card>
      </div>

      {/* ── Parcel Details Modal ──────────────────────────────────────────── */}
      <Modal
        isOpen={!!selectedParcel}
        onClose={closeModal}
        title="Parcel Details"
        size="lg"
        footer={<Button variant="secondary" onClick={closeModal}>Close</Button>}
      >
        {selectedParcel && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-500">Parcel Number</p>
                  <p className="font-medium text-white">{selectedParcel.upi}</p>
                </div>
              </div>

              {selectedParcel.title_deed_number && (
                <div className="flex items-start gap-3">
                  <FileText className="w-5 h-5 text-slate-400 mt-0.5" />
                  <div>
                    <p className="text-xs text-slate-500">Title Deed Number</p>
                    <p className="font-medium text-white">{selectedParcel.title_deed_number}</p>
                  </div>
                </div>
              )}

              <div className="flex items-start gap-3">
                <User className="w-5 h-5 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-500">Owner</p>
                  <p className="font-medium text-white">{selectedParcel.owner_name}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Ruler className="w-5 h-5 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-500">Area (sqm)</p>
                  <p className="font-medium text-white">{formatNumber(selectedParcel.area_sqm)}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <DollarSign className="w-5 h-5 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-500">Valuation</p>
                  <p className="font-medium text-white">
                    {selectedParcel.valuation ? `${formatNumber(selectedParcel.valuation)} RWF` : 'Not Valued'}
                  </p>
                </div>
              </div>

              {selectedParcel.valuation_date && (
                <div className="flex items-start gap-3">
                  <Calendar className="w-5 h-5 text-slate-400 mt-0.5" />
                  <div>
                    <p className="text-xs text-slate-500">Valuation Date</p>
                    <p className="font-medium text-white">{formatDate(selectedParcel.valuation_date)}</p>
                  </div>
                </div>
              )}
            </div>

            {selectedParcel.parish_name && (
              <div>
                <p className="text-xs text-slate-500">Parish</p>
                <p className="font-medium text-white">{selectedParcel.parish_name}</p>
              </div>
            )}

            {selectedParcel.land_use_category_name && (
              <div>
                <p className="text-xs text-slate-500">Land Use Category</p>
                <p className="font-medium text-white">{selectedParcel.land_use_category_name}</p>
              </div>
            )}

            {selectedParcel.location_description && (
              <div>
                <p className="text-xs text-slate-500">Location Description</p>
                <p className="font-medium text-white">{selectedParcel.location_description}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </PageContainer>
  );
}