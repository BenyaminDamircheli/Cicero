"use client";

import React, { useEffect, useState } from 'react';
import Map, { Source, Layer, Popup } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface Source {
  title: string;
  body: string;
  url: string;
}

interface GroupedComplaint {
  id: string;
  coordinates: number[];
  sources: Source[];
}

const MapboxExample = () => {
  const [groupedComplaints, setGroupedComplaints] = useState<GroupedComplaint[]>([]);
  const [viewState, setViewState] = useState({
    longitude: -79.38,
    latitude: 43.6517,
    zoom: 11
  });
  const [popupInfo, setPopupInfo] = useState<GroupedComplaint | null>(null);
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
    <main className='h-screen w-screen relative'>
      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        style={{width: '100%', height: '100%'}}
        attributionControl={false}
        mapStyle="mapbox://styles/mapbox/light-v11"
        mapboxAccessToken='pk.eyJ1IjoiYmRhbWlyY2giLCJhIjoiY20yNzR2eHpxMGZyZzJqcHc0aDJhMHNjbyJ9.o4vtVo0Jvyxy4SBju_waYQ'
        interactiveLayerIds={[layerId]}
        onClick={(e) => {
          const feature = e.features && e.features[0];
          if (feature && feature.properties) {
            const complaint = groupedComplaints.find(c => c.id === feature.properties.id);
            if (complaint) {
              setPopupInfo(complaint);
            }
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

        {popupInfo && (
          <Popup
            longitude={popupInfo.coordinates[1]}
            latitude={popupInfo.coordinates[0]}
            onClose={() => setPopupInfo(null)}
            closeOnClick={false}
          >
            <h3>Complaints</h3>
            {popupInfo.sources.map((source, index) => (
              <div key={index}>
                <h4>{source.title}</h4>
              </div>
            ))}
          </Popup>
        )}
      </Map>
      {isLoading && (
        <div className="absolute top-4 right-4 flex gap-2 items-center justify-center bg-white p-2 rounded-lg">
          <p className="text-black">Loading complaints</p>
          <div className="spinner"></div>
        </div>
      )}
    </main>
  );
};

export default MapboxExample;
