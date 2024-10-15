export interface Source {
    title: string;
    body: string;
    url: string;
  }
  
export interface GroupedComplaint {
    id: string;
    coordinates: number[];
    sources: Source[];
}