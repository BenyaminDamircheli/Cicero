import { useState, useEffect, useRef } from 'react';
import { Building2, X } from 'lucide-react';
import { ProposalInput, GroupedComplaint } from '../../types';
import AIAgentTask from './agentTasks';
import ProposalVisualization from './proposalVisualization';
import Markdown from "react-markdown"
import remarkGfm from 'remark-gfm'

interface ProposalDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  complaint: GroupedComplaint | null;
  location: string;
  coordinates: number[];
  summary: string;
  solution_outline: string;
}

const ProposalDrawer = ({ isOpen, onClose, complaint, location, coordinates, summary, solution_outline }: ProposalDrawerProps) => {
  const [proposal, setProposal] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const clientId = useRef(Math.random().toString(36).substring(7));

  const generateProposal = async () => {
    setIsLoading(true);

    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      wsRef.current = new WebSocket(`ws://localhost:8000/ws/proposal/${clientId.current}`);

      wsRef.current.onopen = () => {
        console.log("WebSocket connected in ProposalDrawer")
      }

      wsRef.current.onerror = (error) => {
        console.error("WebSocket error in ProposalDrawer:", error)
      }
    }

    try {
      const proposalInput: ProposalInput = {
        location: complaint?.location || '',
        coordinates: coordinates || [41.8781, -79.6298],
        summary: summary || '',
        solution_outline: solution_outline || ''
      };

      const response = await fetch(`http://localhost:8000/api/proposals/generate/${clientId.current}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(proposalInput),
      });
      const data = await response.json();
      setProposal(data.proposal.proposal);
    } catch (error) {
      console.error('Error generating proposal:', error);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    if (isOpen && complaint) {
      generateProposal();
    }
    return () => {
      wsRef.current?.close();
    };
  }, [isOpen, complaint]);

  if (!isOpen) return null;

  return (
    <div className="w-[400px] bg-white h-full rounded-md shadow-md border-l-2 border-neutral-200 p-6 relative overflow-y-auto">
      <div className='flex items-center justify-between mb-4'>
        <h1 className='text-lg font-semibold'>Proposal</h1>
        <button onClick={onClose}>
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="space-y-4">
        <AIAgentTask wsRef={wsRef} clientId={clientId.current} />
      </div>
      {!isLoading && proposal && (
        <div className="flex flex-col gap-4">
          <div className="text-md font-semibold text-neutral-600">
            Written Proposal
          </div>
          <div className="max-w-none prose">
            <Markdown 
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({node, ...props}) => <h1 className="text-xl font-bold mb-5" {...props}/>,
                h2: ({node, ...props}) => <h2 className="text-xl font-bold mb-4" {...props}/>,
                h3: ({node, ...props}) => <h3 className="text-lg font-bold mb-3" {...props}/>,
                p: ({node, ...props}) => <p className="mb-4 leading-relaxed" {...props}/>,
                ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-4" {...props}/>,
                ol: ({node, ...props}) => <ol className="list-decimal pl-5 mb-4" {...props}/>,
                li: ({node, ...props}) => <li className="mb-1" {...props}/>,
              }}
            >
              {proposal}
            </Markdown>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProposalDrawer;
