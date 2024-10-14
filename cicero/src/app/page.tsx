import Image from "next/image";
import dynamic from "next/dynamic";

const MapComponent = dynamic(() => import("./components/map"), { ssr: false });

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <div className="flex flex-col items-center justify-center h-screen">
        <h1 className="text-4xl font-bold">Complaints Map</h1>
        <MapComponent />
      </div>
    </div>
  );
}
