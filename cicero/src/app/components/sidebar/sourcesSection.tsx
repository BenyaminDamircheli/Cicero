import React, {useState, useEffect} from 'react';
import { BookOpen, ChevronDown, ChevronUp, Icon, Info } from 'lucide-react';
import { Source } from '../types';
import { SourceComponent } from './source';

interface SourcesSectionProps {
    sources: Source[];
    title: string;
    icon: React.ElementType;
}

const SourcesSection = ({ sources, title, icon }: SourcesSectionProps) => {
    const [isOpen, setIsOpen] = useState(false);
    
    const toggleOpen = () => {
        setIsOpen(!isOpen);
    };

    return (
        <section>
            <div className='flex justify-between items-center'>
                <h3 className="text-md flex items-center font-semibold mb-2">
                    {React.createElement(icon, { className: "inline-block mr-2 w-[12px] h-[12px]" })}
                    {title}
                </h3>
                <button onClick={toggleOpen} className='p-[2px] rounded-md bg-gray-100 hover:bg-gray-200'>
                    {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>
            </div>
            {isOpen && (
                <div className="grid grid-cols-2 gap-2">
                    {sources.map((source, index) => (
                        <a href={source.url} target="_blank" rel="noopener noreferrer" key={index} className="bg-gray-100 p-3 rounded-md hover:bg-gray-200 transition-colors duration-200">
                            <SourceComponent source={source} />
                        </a>
                    ))} 
                </div>
            )}  
        </section>
    )
}

export default SourcesSection;
