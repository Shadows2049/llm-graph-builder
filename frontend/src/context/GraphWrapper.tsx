import { createContext, useState, useContext, FC } from 'react';
import { GraphContextType, ExtendedNode, ExtendedRelationship, GraphContextProviderProps } from '../types';

const GraphContext = createContext<GraphContextType | undefined>(undefined);

const GraphContextWrapper: FC<GraphContextProviderProps> = ({ children }) => {
  const [nodes, setNodes] = useState<ExtendedNode[]>([]);
  const [relationships, setRelationships] = useState<ExtendedRelationship[]>([]);
  const [viewPoint, setViewPoint] = useState<string>('tableView');
  const [openGraphView, setOpenGraphView] = useState<boolean>(false);
  const [isGraphLoading, setIsGraphLoading] = useState(false);

  const value: GraphContextType = {
    nodes,
    setNodes,
    relationships,
    setRelationships,
    viewPoint,
    setViewPoint,
    openGraphView,
    setOpenGraphView,
    isGraphLoading,
    setIsGraphLoading,
  };
  return <GraphContext.Provider value={value}>{children}</GraphContext.Provider>;
};
const useGraphContext = () => {
  const context = useContext(GraphContext);
  if (!context) {
    throw new Error('useGraphContext must be used within a GraphContextWrapper');
  }
  return context;
};
export { GraphContextWrapper, useGraphContext };
