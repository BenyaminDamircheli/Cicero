import React from 'react'
import { GroupedComplaint } from '../types';
import { Info, Globe, BookOpen, Building2, Hammer } from 'lucide-react';
import dynamic from 'next/dynamic';
import SidebarSection from './sidebarSection';

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
        <SidebarSection title='Summary' icon={Globe} content='Downtown Toronto, particularly around Yonge and Dundas Square, is facing significant challenges with homelessness, sanitation, and public safety issues such as drug use. The area has seen an increase in encampments and improper waste disposal, contributing to unsanitary conditions and health concerns. Public spaces are impacted by these issues, affecting overall livability and tourism in the city center.'/>
      </section>

      <section className="mb-6">
        <SidebarSection title='Urgency' icon={Info} content="The combination of homelessness and poor sanitation poses an immediate risk to public health and safety, requiring swift intervention to address the living conditions of the homeless population and improve the cleanliness of public spaces." />
      </section>

      <section className="mb-6">
        <SidebarSection title="Sources" icon={BookOpen} sources={selectedComplaint.sources} />
      </section>

      <section className="mb-6">
        <SidebarSection title="Improvements" icon={Hammer} content='The city should implement a comprehensive plan to address the root causes of homelessness and improve sanitation in the area. This includes providing affordable housing, mental health support, and addiction treatment services. Additionally, regular cleanups and maintenance of public spaces should be implemented to ensure the area remains clean and safe for residents and visitors.' />
      </section>

    </div>
  )
}  

export default SidebarContent