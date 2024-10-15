"use client"
import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import { GroupedComplaint } from '../types';

interface RevolvingMapProps {
    complaint: GroupedComplaint;
}

import 'mapbox-gl/dist/mapbox-gl.css';

const RevolvingMap = ({ complaint }: RevolvingMapProps) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    mapboxgl.accessToken = 'pk.eyJ1IjoiYmRhbWlyY2giLCJhIjoiY20yNzR2eHpxMGZyZzJqcHc0aDJhMHNjbyJ9.o4vtVo0Jvyxy4SBju_waYQ';

    mapRef.current = new mapboxgl.Map({
      style: 'mapbox://styles/mapbox/outdoors-v12',
      center: [complaint.coordinates[1], complaint.coordinates[0]],
      zoom: 15.5,
      pitch: 45,
      bearing: 0,
      container: 'map',
      antialias: true,
      attributionControl: false,
    });

    mapRef.current?.on('style.load', () => {
      const layers = mapRef.current?.getStyle()?.layers;
      const labelLayerId = layers?.find(
        (layer: any) => layer.type === 'symbol' && layer.layout['text-field']
      )?.id;

      mapRef.current?.addLayer(
        {
          id: 'add-3d-buildings',
          source: 'composite',
          'source-layer': 'building',
          filter: ['==', 'extrude', 'true'],
          type: 'fill-extrusion',
          minzoom: 15,
          paint: {
            'fill-extrusion-color': '#aaa',
            'fill-extrusion-height': [
              'interpolate',
              ['linear'],
              ['zoom'],
              15,
              0,
              15.05,
              ['get', 'height']
            ],
            'fill-extrusion-base': [
              'interpolate',
              ['linear'],
              ['zoom'],
              15,
              0,
              15.05,
              ['get', 'min_height']
            ],
            'fill-extrusion-opacity': 0.6
          }
        },
        labelLayerId
      );

      // Rotating the map
      let bearing = 0;
      function rotateCamera() {
        bearing += 0.1; 
        mapRef.current?.setBearing(bearing % 360);
        requestAnimationFrame(rotateCamera);
      }
      rotateCamera();
    });

    return () => mapRef.current?.remove();
  }, [complaint.coordinates]);

  return <div id="map" ref={mapContainerRef} style={{ height: '100%' }}></div>;
};

export default RevolvingMap;
