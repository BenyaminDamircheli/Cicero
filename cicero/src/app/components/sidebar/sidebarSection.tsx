import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Source } from '../types';
import { SourceComponent } from './source';

interface SidebarSectionProps {
    title: string | null;
    icon: React.ElementType;
    content?: string | null;
    sources?: Source[];
    urgency?: number | null;
    loading?: boolean;
}

const SidebarSection = ({ title, icon, content, sources, urgency, loading }: SidebarSectionProps) => {
    const [isOpen, setIsOpen] = useState(true);
    
    const toggleOpen = () => {  
        setIsOpen(!isOpen);
    };

    return (
        <section className="mb-4">
            <div className='flex justify-between items-center'>
                <h3 className="text-md flex items-center font-semibold mb-2">
                    {React.createElement(icon, { className: "inline-block mr-2 w-[12px] h-[12px]" })}
                    {title}
                </h3>
                <button onClick={toggleOpen} className='p-[2px] rounded-md bg-gray-100 hover:bg-gray-200'>
                    {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-[18px] h-[18px]" />}
                </button>
            </div>
            {isOpen && (
                <div>
                    {content && (
                        <p className="text-sm text-gray-700 mb-2">
                            {content}
                        </p>
                    )}
                    {urgency && (
                        <p className="text-sm text-gray-700 mb-2">
                            Urgency: {urgency}
                        </p>
                    )}
                    {sources && (
                        <div className="grid grid-cols-2 gap-2">
                            {sources.map((source, index) => (
                                <a href={source.url} target="_blank" rel="noopener noreferrer" key={index} className="bg-gray-100 p-3 rounded-md hover:bg-gray-200 transition-colors duration-200">
                                    <SourceComponent source={source} />
                                </a>
                            ))} 
                        </div>
                    )}
                </div>
            )}  
        </section>
    )
}

export default SidebarSection;
