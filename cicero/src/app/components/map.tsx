"use client";

import React, { useEffect, useState } from 'react';
import Map, { Source, Layer, Popup } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { GroupedComplaint } from './types';
import { Loader, Loader2 } from 'lucide-react';

interface MapComponentProps {
  onMarkerSelect: (complaint: GroupedComplaint | null) => void;
}

const MapComponent = ({ onMarkerSelect }: MapComponentProps) => {
  const [groupedComplaints, setGroupedComplaints] = useState<GroupedComplaint[]>([]);
  const [viewState, setViewState] = useState({
    longitude: -79.38,
    latitude: 43.6517,
    zoom: 11
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchGroupedComplaints = async () => {
      try {
        console.log("Fetching complaints")
        const response = await fetch('http://localhost:8000/api/complaints');
        const data = await response.json();
        console.log(data)
        setGroupedComplaints(data);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching complaints:', error);
      }
    };

    fetchGroupedComplaints();
  }, []);

  const geojson = {
    type: 'FeatureCollection',
    features: groupedComplaints.map(complaint => ({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [complaint.coordinates[1], complaint.coordinates[0]]
      },
      properties: {
        id: complaint.id,
        sources: complaint.sources
      }
    }))
  };

  const layerId = "complaints-layer";

  return (
    <div className='h-full w-full inset-0 rounded-md overflow-hidden'>
      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        style={{width: '100%', height: '100%'}}
        attributionControl={false}
        mapStyle="mapbox://styles/mapbox/satellite-streets-v12"
        mapboxAccessToken='pk.eyJ1IjoiYmRhbWlyY2giLCJhIjoiY20yNzR2eHpxMGZyZzJqcHc0aDJhMHNjbyJ9.o4vtVo0Jvyxy4SBju_waYQ'
        interactiveLayerIds={[layerId]}
        onClick={(e) => {
          const feature = e.features && e.features[0];
          if (feature && feature.properties) {
            const complaint = groupedComplaints.find(c => c.id === feature.properties?.id);
            if (complaint) {
              onMarkerSelect(complaint);
            }
          } else {
            onMarkerSelect(null);
          }
        }}
        onMouseEnter={() => {
          document.body.style.cursor = 'pointer';
        }}
        onMouseLeave={() => {
          document.body.style.cursor = '';
        }}
      >
        {!isLoading && (
          <Source id="complaints" type="geojson" data={geojson}>
            <Layer
              id={layerId}
              type="circle"
              paint={{
                'circle-color': '#11b4da',
                'circle-radius': 8,
                'circle-stroke-width': 1,
                'circle-stroke-color': '#fff'
              }}
            />
          </Source>
        )}
      </Map>
      {isLoading && (
        <div className="absolute top-4 right-4 text-xs flex gap-2 items-center justify-center bg-white p-2 rounded-md">
          <p className="text-black">Loading</p>
          <Loader2 className="animate-spin w-3 h-3" />
        </div>
      )}
    </div>
  );
};

export default MapComponent;
