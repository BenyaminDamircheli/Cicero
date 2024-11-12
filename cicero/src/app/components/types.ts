export interface Source {
    title: string;
    body: string;
    url: string;
  }
  
export interface GroupedComplaint {
    id: string;
    coordinates: number[];
    sources: Source[];
    location: string;
    summary: string;
    solution_outline: string;
}

export interface ProposalInput {
    location: string;
    coordinates: number[];
    summary: string;
    solution_outline: string;
}