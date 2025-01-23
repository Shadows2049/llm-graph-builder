import React from 'react';
import { Button } from '@neo4j-ndl/react';
import GraphViewModal from './GraphViewModal';
import { GraphViewButtonProps } from '../../types';
import { useGraphContext } from '../../context/GraphWrapper';

const GraphViewButton: React.FC<GraphViewButtonProps> = ({ nodeValues, relationshipValues, fill, label, handleClick }) => {
  const { openGraphView, setOpenGraphView, viewPoint } = useGraphContext();
  return (
    <>
      <Button fill={fill} onClick={handleClick} style={{}}>
        {label}
      </Button>
      <GraphViewModal
        open={openGraphView}
        setGraphViewOpen={setOpenGraphView}
        viewPoint={viewPoint}
        nodeValues={nodeValues}
        relationshipValues={relationshipValues}
      />
    </>
  );
};
export default GraphViewButton;
