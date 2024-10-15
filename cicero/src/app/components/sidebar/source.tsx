import { Source } from "../types";
import { Globe } from "lucide-react";

interface SourceProps {
    source: Source;
}

export const SourceComponent: React.FC<SourceProps> = ({ source }) => {
    const url = source.url;
    const domain = url.split('://')[1].split('/')[0];
    return (
        <div className="w-[150px] h-[50px] justify-between">
            <div className="flex items-center">
                <Globe className="inline-block mr-2 w-[12px] h-[12px]" />
                <p className="text-sm">{domain}</p>
            </div>
        </div>
    );
};