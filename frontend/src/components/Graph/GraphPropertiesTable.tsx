import { GraphLabel, Typography } from '@neo4j-ndl/react';
import { GraphPropertiesTableProps } from '../../types';

const GraphPropertiesTable = ({ propertiesWithTypes }: GraphPropertiesTableProps): JSX.Element => {
  return (
    <div className='flex w-full flex-col break-all px-4 text-sm' data-testid='viz-details-pane-properties-table'>
      <div className='mb-1 flex flex-row pl-2'>
        <Typography variant='body-medium' className='basis-1/3'>
          Key
        </Typography>
        <Typography variant='body-medium'>Value</Typography>
      </div>
      {propertiesWithTypes.map(({ key, value }, _) => {
        const isObject = value && typeof value === 'object' && 'low' in value && 'high' in value;
        return (
          <div key={key} className='border-palette-neutral-border-weak flex border-t py-1 pl-2 first:border-none'>
            <div className='shrink basis-1/3 overflow-hidden whitespace-nowrap'>
              <GraphLabel
                type='propertyKey'
                className='pointer-events-none !max-w-full overflow-ellipsis'
                htmlAttributes={{
                  tabIndex: -1,
                }}
              >
                {key}
              </GraphLabel>
            </div>
            <div className={`ml-2 flex-1 whitespace-pre-wrap`}>
              {isObject ? (
                <div>
                  <span className="block">{value.low}</span>
                </div>
              ) : (
                <span>{value}</span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default GraphPropertiesTable;
