import React, { useEffect, useState } from 'react'
import { GroupedComplaint } from '../types';
import { Info, Globe, BookOpen, Building2, Hammer } from 'lucide-react';
import dynamic from 'next/dynamic';
import SidebarSection from './sidebarSection';

const RevolvingMap = dynamic(() => import('./revolvingMap'), { ssr: false });


interface SidebarContentProps {
    selectedComplaint: GroupedComplaint | null;
}


const SidebarContent = ({ selectedComplaint }: SidebarContentProps) => {
  const [title, setTitle] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [urgencyNumber, setUrgencyNumber] = useState<number | null>(null);
  const [urgencyExplanation, setUrgencyExplanation] = useState<string | null>(null);
  const [improvements, setImprovements] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    setLoading(true);
    if (selectedComplaint) {
      fetchComplaintSummary();
    } else {
      setTitle(null);
      setSummary(null);
      setUrgencyNumber(null);
      setUrgencyExplanation(null);
      setImprovements(null);
    }
  }, [selectedComplaint]);


  const fetchComplaintSummary = async () => {
    setLoading(true);
    console.log("Fetching complaint summary");
    const response = await fetch('http://localhost:8000/api/complaints/summary', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(selectedComplaint),
    });
    const data = await response.json();
    setTitle(data.title);
    setSummary(data.summary);
    setUrgencyNumber(data.urgency.score);
    setUrgencyExplanation(data.urgency.explanation);
    setImprovements(data.solutions);
    setLoading(false);
  };

  if (!selectedComplaint) {
    return (
        <div className="flex-grow flex items-center justify-center">
            <p className='text-center text-gray-500 text-sm'>No marker selected</p>
        </div>
    )
  }

  return(
    <div className="pt-4">
      {loading ? (
        <div className="h-6 w-3/4 bg-gray-200 rounded animate-pulse mb-4"></div>
      ) : (
        <h1 className='text-lg font-bold mb-4 truncate'>{title}</h1>
      )}
      <section className='mb-6 rounded-md overflow-hidden'>
        <div className='h-[200px]'>
          <RevolvingMap complaint={selectedComplaint} />
        </div>
      </section>

      {/* Summary Section */}
      <section className="mb-6">
        {loading ? (
          <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
        ) : (
          <SidebarSection title='Summary' icon={Globe} content={summary}/>
        )}
      </section>

      {/* Urgency Section */}
      <section className="mb-6">
        {loading ? (
          <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
        ) : (
          <SidebarSection title='Urgency' icon={Info} content={urgencyExplanation} urgency={urgencyNumber} />
        )}
      </section>

      {/* Sources Section */}
      <section className="mb-6">
        {loading ? (
          <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
        ) : (
          <SidebarSection title="Sources" icon={BookOpen} sources={selectedComplaint.sources} />
        )}
      </section>

      {/* Improvements Section */}
      <section className="mb-6">
        {loading ? (
          <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
        ) : (
          <SidebarSection title="Improvements" icon={Hammer} content={improvements} />
        )}
      </section>

    </div>
  )
}  

export default SidebarContent