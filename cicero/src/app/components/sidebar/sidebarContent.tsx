import React from 'react'
import { GroupedComplaint } from '../types';
import { Info, Globe, BookOpen, Building2 } from 'lucide-react';
import dynamic from 'next/dynamic';
import SourcesSection from './sourcesSection';

const RevolvingMap = dynamic(() => import('./revolvingMap'), { ssr: false });


interface SidebarContentProps {
    selectedComplaint: GroupedComplaint | null;
}


const SidebarContent = ({ selectedComplaint }: SidebarContentProps) => {
  if (!selectedComplaint) {
    return (
        <div className="flex-grow flex items-center justify-center">
            <p className='text-center text-gray-500 text-sm'>No marker selected</p>
        </div>
    )
  }

  return(
    <div className="pt-4">
      <section className='mb-6 rounded-md overflow-hidden'>
        <div className='h-[200px]'>
          <RevolvingMap complaint={selectedComplaint} />
        </div>
      </section>

      <section className="mb-6">
        <h3 className="text-md flex items-center font-semibold mb-2">
            <Globe className="inline-block mr-2 w-[12px] h-[12px]" />
            Summary
        </h3>
        <p className="text-sm text-gray-700">
          Downtown Toronto, particularly around Yonge and Dundas Square, is facing significant challenges with homelessness, sanitation, and public safety issues such as drug use. The area has seen an increase in encampments and improper waste disposal, contributing to unsanitary conditions and health concerns. Public spaces are impacted by these issues, affecting overall livability and tourism in the city center.
        </p>
      </section>

      <section className="mb-6">
        <h3 className="text-md flex items-center font-semibold mb-2">
            <Info className="inline-block mr-2 w-[12px] h-[12px]" />
            Urgency
        </h3>
        <p className="text-sm text-gray-700">
          The combination of homelessness and poor sanitation poses an immediate risk to public health and safety, requiring swift intervention to address the living conditions of the homeless population and improve the cleanliness of public spaces.
        </p>
      </section>

      <SourcesSection sources={selectedComplaint.sources} title="Sources" icon={BookOpen} />

    </div>
  )
}  

export default SidebarContent