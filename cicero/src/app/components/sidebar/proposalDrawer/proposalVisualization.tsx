import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import type { GroupedComplaint } from '../../types';
import type { GeoJSON } from 'geojson';

interface ProposalVisualizationProps {
  complaint: GroupedComplaint | null;
  proposalType: 'park' | 'building' | 'infrastructure' | undefined;
}

const ProposalVisualization = ({ complaint, proposalType }: ProposalVisualizationProps) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    mapboxgl.accessToken = 'pk.eyJ1IjoiYmRhbWlyY2giLCJhIjoiY20yNzR2eHpxMGZyZzJqcHc0aDJhMHNjbyJ9.o4vtVo0Jvyxy4SBju_waYQ';

    mapRef.current = new mapboxgl.Map({
      style: 'mapbox://styles/mapbox/satellite-v9',
      center: [complaint?.coordinates[1] ?? 0, complaint?.coordinates[0] ?? 0],
      zoom: 17,
      pitch: 60,
      bearing: 0,
      container: 'proposal-map',
      antialias: true,
    });

    mapRef.current?.on('style.load', () => {
      // Add custom layer for proposal visualization
      mapRef.current?.addLayer({
        id: 'proposal-layer',
        type: 'fill-extrusion',
        source: {
          type: 'geojson',
          data: generateProposalGeometry(proposalType ?? '', complaint?.coordinates ?? [])
        },
        paint: {
          'fill-extrusion-color': proposalType === 'park' ? '#2ecc71' : '#3498db',
          'fill-extrusion-height': proposalType === 'building' ? 30 : 2,
          'fill-extrusion-opacity': 0.8,
          'fill-extrusion-base': 0
        }
      });

      // Rotate camera slowly
      let bearing = 0;
      function rotateCamera() {
        bearing += 0.1;
        mapRef.current?.setBearing(bearing % 360);
        requestAnimationFrame(rotateCamera);
      }
      rotateCamera();
    });

    return () => mapRef.current?.remove();
  }, [complaint?.coordinates, proposalType]);

  return (
    <div 
      id="proposal-map" 
      ref={mapContainerRef} 
      className="w-full h-[200px] rounded-lg overflow-hidden"
    />
  );
};

// Helper function to generate GeoJSON for different proposal types
const generateProposalGeometry = (type: string, coordinates: number[]): GeoJSON.FeatureCollection => {
  const radius = 0.001;
  const points = 32;
  const features: GeoJSON.Feature[] = [];

  if (type === 'park') {
    features.push({
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        coordinates: [[...Array(points)].map((_, i) => {
          const angle = (i / points) * Math.PI * 2;
          return [
            coordinates[1] + Math.cos(angle) * radius,
            coordinates[0] + Math.sin(angle) * radius
          ];
        })]
      },
      properties: {}
    });
  }

  return {
    type: 'FeatureCollection',
    features
  } as const;
};

export default ProposalVisualization;
