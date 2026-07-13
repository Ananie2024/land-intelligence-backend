// WKB Parser Utility
// Land Intelligence System - Parses hex-encoded Well-Known Binary geometry to GeoJSON coordinates

/**
 * Parses a hex-encoded WKB (Well-Known Binary) string to coordinate arrays
 * Supports Point, LineString, Polygon, and MultiPolygon geometry types
 * 
 * WKB Format:
 * - Byte 0: Byte order (0 = big-endian, 1 = little-endian)
 * - Bytes 1-4: Geometry type (uint32)
 * - Polygon:
 *   - Bytes 5-8: Number of rings (uint32)
 *   - For each ring:
 *     - Bytes N-N+3: Number of points (uint32)
 *     - Bytes N+4+: Point coordinates (double X, double Y for each point)
 * - MultiPolygon:
 *   - Bytes 5-8: Number of polygons (uint32)
 *   - For each sub-polygon:
 *     - Bytes N: Byte order (uint8)
 *     - Bytes N+1-N+4: Geometry type (uint32)
 *     - Bytes N+5-N+8: Number of rings (uint32)
 *     - For each ring:
 *       - Bytes N-N+3: Number of points (uint32)
 *       - Bytes N+4+: Point coordinates (double X, double Y for each point)
 */

// WKB geometry type constants
const WKB_TYPES = {
  POINT: 1,
  LINESTRING: 2,
  POLYGON: 3,
  MULTIPOINT: 4,
  MULTILINESTRING: 5,
  MULTIPOLYGON: 6,
  GEOMETRYCOLLECTION: 7,
} as const;

/**
 * Convert hex string to Uint8Array
 */
function hexToBytes(hex: string): Uint8Array {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
  }
  return bytes;
}

/**
 * Parse a WKB hex string to coordinate array
 * Returns array of polygon rings, where each ring is an array of [lng, lat] coordinates
 */
export function parseWkbToCoordinates(wkbHex: string | null | undefined): [number, number][][] {
  if (!wkbHex) return [];
  
  try {
    // Remove any whitespace
    const hex = wkbHex.trim();
    
    // Parse the hex string to bytes
    const bytes = hexToBytes(hex);
    const view = new DataView(bytes.buffer);
    
    // Read byte order (0 = big-endian, 1 = little-endian)
    const byteOrder = view.getUint8(0);
    const littleEndian = byteOrder === 1;
    
    // Read geometry type (4 bytes after byte order)
    const geometryType = view.getUint32(1, littleEndian);
    
    // Position starts after byte order (1 byte) + geometry type (4 bytes)
    let pos = 5;
    
    switch (geometryType) {
      case WKB_TYPES.POINT: {
        // Point: X (8 bytes), Y (8 bytes)
        const x = view.getFloat64(5, littleEndian);
        const y = view.getFloat64(13, littleEndian);
        // Return single point as a polygon ring (for consistency with Leaflet)
        return [[[x, y]]];
      }
        
      case WKB_TYPES.LINESTRING: {
        // LineString: number of points (uint32), then points
        const pointCount = view.getUint32(pos, littleEndian);
        pos += 4;
        
        const ring: [number, number][] = [];
        for (let i = 0; i < pointCount; i++) {
          const x = view.getFloat64(pos, littleEndian);
          const y = view.getFloat64(pos + 8, littleEndian);
          ring.push([x, y]);
          pos += 16;
        }
        return [ring];
      }
        
      case WKB_TYPES.POLYGON: {
        // Polygon: number of rings, then each ring
        const ringCount = view.getUint32(pos, littleEndian);
        pos += 4;
        
        const rings: [number, number][][] = [];
        for (let r = 0; r < ringCount; r++) {
          const pointCount = view.getUint32(pos, littleEndian);
          pos += 4;
          
          const ring: [number, number][] = [];
          for (let p = 0; p < pointCount; p++) {
            const x = view.getFloat64(pos, littleEndian);
            const y = view.getFloat64(pos + 8, littleEndian);
            ring.push([x, y]);
            pos += 16;
          }
          rings.push(ring);
        }
        return rings;
      }
        
      case WKB_TYPES.MULTIPOLYGON: {
        // MultiPolygon: number of polygons, each with rings
        // Each sub-polygon has its own 5-byte header (byte order + geometry type)
        const polyCount = view.getUint32(pos, littleEndian);
        pos += 4;
        
        const allRings: [number, number][][] = [];
        for (let poly = 0; poly < polyCount; poly++) {
          // Skip sub-polygon header: byte order (1 byte) + geometry type (4 bytes)
          pos += 5;
          
          const ringCount = view.getUint32(pos, littleEndian);
          pos += 4;
          
          for (let r = 0; r < ringCount; r++) {
            const pointCount = view.getUint32(pos, littleEndian);
            pos += 4;
            
            const ring: [number, number][] = [];
            for (let p = 0; p < pointCount; p++) {
              const x = view.getFloat64(pos, littleEndian);
              const y = view.getFloat64(pos + 8, littleEndian);
              ring.push([x, y]);
              pos += 16;
            }
            allRings.push(ring);
          }
        }
        return allRings;
      }
        
      default:
        console.warn(`Unsupported WKB geometry type: ${geometryType}`);
        return [];
    }
  } catch (error) {
    console.error('Failed to parse WKB:', error);
    return [];
  }
}

export default parseWkbToCoordinates;