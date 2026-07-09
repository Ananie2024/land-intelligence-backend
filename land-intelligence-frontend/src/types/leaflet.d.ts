// TypeScript declarations for Leaflet
declare module 'leaflet' {
  export class LatLng {
    constructor(lat: number, lng: number);
    lat: number;
    lng: number;
  }
  
  export class LatLngBounds {
    constructor(...latlngs: LatLng[]);
  }

  export namespace Icon {
    namespace Default {
      const mergeOptions: (options: {
        iconRetinaUrl?: string;
        iconUrl?: string;
        shadowUrl?: string;
      }) => void;
    }
  }
}