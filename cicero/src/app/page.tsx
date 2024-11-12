"use client";

import dynamic from "next/dynamic";
import Sidebar from "./components/sidebar/sidebar";
import { useState } from "react";
import { GroupedComplaint } from "./components/types";

const MapComponent = dynamic(() => import("./components/map"), { ssr: false });

export default function Home() {
  const [selectedComplaint, setSelectedComplaint] = useState<GroupedComplaint | null>(null);

  const handleUpdateComplaint = (updatedComplaint: GroupedComplaint) => {
    setSelectedComplaint(updatedComplaint);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="pt-[6px] pl-[6px] pb-[6px]">
        <Sidebar 
          selectedComplaint={selectedComplaint} 
          onUpdateComplaint={handleUpdateComplaint} 
        />
      </div>
      <div className="flex-grow p-[6px]">
          <MapComponent onMarkerSelect={setSelectedComplaint} />
      </div>
    </div>
  );
}
