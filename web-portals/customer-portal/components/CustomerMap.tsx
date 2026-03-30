'use client';

import { useState, useRef, useMemo, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for Next.js missing Leaflet marker icons
const customIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

// Component to auto-center the map when coordinates change
function RecenterAutomatically({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lng]);
  }, [lat, lng, map]);
  return null;
}

interface CustomerMapProps {
  initialLat: number;
  initialLng: number;
  onLocationChange: (lat: number, lng: number) => void;
}

export default function CustomerMap({ initialLat, initialLng, onLocationChange }: CustomerMapProps) {
  const [position, setPosition] = useState({ lat: initialLat, lng: initialLng });
  const markerRef = useRef<L.Marker>(null);

  const eventHandlers = useMemo(
    () => ({
      dragend() {
        const marker = markerRef.current;
        if (marker != null) {
          const newPos = marker.getLatLng();
          setPosition(newPos);
          onLocationChange(newPos.lat, newPos.lng);
        }
      },
    }),
    [onLocationChange]
  );

  return (
    <MapContainer 
      center={[position.lat, position.lng]} 
      zoom={16} 
      style={{ height: '100%', width: '100%', zIndex: 0 }}
      zoomControl={false}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />
      <Marker
        draggable={true}
        eventHandlers={eventHandlers}
        position={position}
        ref={markerRef}
        icon={customIcon}
      />
      <RecenterAutomatically lat={position.lat} lng={position.lng} />
    </MapContainer>
  );
}