import React from 'react'
import { Libre_Baskerville } from "next/font/google";
import { GroupedComplaint } from '../types';
import SidebarContent from './sidebarContent';
import { Building2 } from "lucide-react";
const libreBaskerville = Libre_Baskerville({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-libre-baskerville",
  style: "italic",
});



interface SidebarProps {
  selectedComplaint: GroupedComplaint | null;
}

const Sidebar = ({ selectedComplaint }: SidebarProps) => {
  return (
    <div className="w-[350px] bg-white shadow-md h-full rounded-md flex flex-col">
        <div className="p-4 overflow-y-auto max-h-full">
            <h1 className={`text-3xl text-center font-bold mb-2 ${libreBaskerville.className}`}>Cicero</h1>
            <p className="text-center text-xs text-gray-500">Tool for turning citizen complaints into actionable government proposals</p>
            <SidebarContent selectedComplaint={selectedComplaint} />
        </div>

      {selectedComplaint && <section className='mt-auto p-4'>
        <button className="bg-black text-white px-4 py-2 rounded-md w-full hover:bg-gray-800" disabled={!selectedComplaint}>
          <p className='text-sm flex items-center justify-center'>
            <Building2 className="inline-block mr-2 w-[12px] h-[12px]" />
            Generate Proposal
          </p>
          </button>
        </section>}
    </div>
  )
}

export default Sidebar
