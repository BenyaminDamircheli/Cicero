import React from 'react';
import { Building2, X, Search, Loader2 } from 'lucide-react';
import { GroupedComplaint } from '../../types';
import AIAgentTask from './agentTasks';
import ProposalVisualization from './proposalVisualization';


interface ProposalDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  complaint: GroupedComplaint | null;
  proposalType?: 'park' | 'building' | 'infrastructure' | undefined;

}

const ProposalDrawer = ({ isOpen, onClose, complaint, proposalType }: ProposalDrawerProps) => {
  if (!isOpen) return null;

  return (
    <div className="w-[400px] bg-white h-full rounded-md shadow-md border-l-2 border-neutral-200 p-6 relative">
      <div className='flex items-center justify-between mb-4'>
        <h1 className='text-lg font-semibold'>Proposal</h1>
        <button 
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors duration-200"
        >
          <X strokeWidth={3} className="w-3 h-3 text-gray-500" />
        </button>
      </div>

      <div className='mb-4'>
        <div className='flex items-center space-x-1'>
          <Building2 strokeWidth={3} className="w-3 h-3" />
          <h2 className='font-semibold'>Satelite Image</h2>
        </div>
        <div className='w-full h-[200px] bg-zinc-200 rounded-md'>
          <div className='flex items-center justify-center w-full h-full space-x-2'>
            <h2 className='text-sm text-neutral-600'>Generating satelite image</h2>
            <Loader2 className='w-4 h-4 animate-spin' />
          </div>
        </div>
      </div>
      <div className="flex justify-between items-center">
        <div className='flex items-center space-x-1'>
          <Search strokeWidth={3} className="w-3 h-3" />
          <h2 className="font-semibold">
            Research
          </h2>
        </div>
      </div>
      
      <div className="px-2">
        <AIAgentTask />
      </div>
    </div>
  );
};

export default ProposalDrawer;
