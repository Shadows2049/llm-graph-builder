export const document = `+ [docs]`;

export const chunks = `+ [chunks] + collect { MATCH p=(c)-[:NEXT_CHUNK]->() RETURN p } // chunk-chain
+ collect { MATCH p=(c)-[:SIMILAR]-() RETURN p } // similar-chunks`;

export const entities = `+ collect { OPTIONAL MATCH (c:Chunk)-[:HAS_ENTITY]->(e), p=(e)-[*0..1]-(:!Chunk) RETURN p }`;

export const docEntities = `+ [docs] 
+ collect { MATCH (c:Chunk)-[:HAS_ENTITY]->(e), p=(e)--(:!Chunk) RETURN p }`;

export const docChunks = `+ [chunks] // documents with chunks
+ collect { MATCH p=(c)-[:NEXT_CHUNK]->() RETURN p } // chunk-chain
+ collect { MATCH p=(c)-[:SIMILAR]-() RETURN p } // similar-chunks
+ [docs]`;

export const chunksEntities = `// if chunks:
+ [chunks] // documents with chunks
+ collect { MATCH p=(c)-[:NEXT_CHUNK]->() RETURN p } // chunk-chain
+ collect { MATCH p=(c)-[:SIMILAR]-() RETURN p } // similar-chunks
//chunks with entities
+ collect { OPTIONAL MATCH p=(c:Chunk)-[:HAS_ENTITY]->(e)-[*0..1]-(:!Chunk) RETURN p }`;

export const colors = [
  '#588c7e',
  '#f2e394',
  '#f2ae72',
  '#d96459',
  '#5b9aa0',
  '#d6d4e0',
  '#b8a9c9',
  '#622569',
  '#ddd5af',
  '#d9ad7c',
  '#a2836e',
  '#674d3c',
];
export const llms =
  process.env?.LLM_MODELS?.trim() != ''
    ? process.env.LLM_MODELS?.split(',')
    : ['Diffbot', 'Gemini Pro', 'OpenAI GPT 3.5', 'OpenAI GPT 4'];
export const defaultLLM = llms?.includes('OpenAI GPT 4')
  ? 'OpenAI GPT 4'
  : llms?.includes('Gemini Pro')
  ? 'Gemini Pro'
  : 'Diffbot';
  export const chunkSize = 5 * 1024 * 1024;