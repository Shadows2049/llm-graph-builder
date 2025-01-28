from langchain_experimental.graph_transformers.diffbot import DiffbotGraphTransformer
from langchain_community.graphs import Neo4jGraph
from langchain.docstore.document import Document
from typing import List
import os
import logging

logging.basicConfig(format='%(asctime)s - %(message)s',level='INFO')
def extract_graph_from_diffbot(graph: Neo4jGraph, 
                               chunks: List[Document],
                               file_name : str,
                               isEmbedding : bool,
                               uri : str,
                               userName : str,
                               password : str):
    """ Create knowledge graph using diffbot transformer

    Args:
        graph (Neo4jGraph): Neo4jGraph connection object
        chunks (List[Document]): list of chunk documents created from input file
        file_name (str) : file name of input source
        isEmbedding (bool) : isEmbedding used to create embedding for chunks or not.
        uri: URI of the graph to extract
        userName: Username to use for graph creation ( if None will use username from config file )
        password: Password to use for graph creation ( if None will use password from config file )
        
    Returns: List of langchain GraphDocument - used to generate graph
        
    """    
    diffbot_api_key = os.environ.get('DIFFBOT_API_KEY')
    diffbot_nlp = DiffbotGraphTransformer(diffbot_api_key=diffbot_api_key)
    graph_document_list = []
    
    logging.info(f"create relationship between source,chunk and entity nodes created from Diffbot")
    for chunk in chunks:
        graph_document = diffbot_nlp.convert_to_graph_documents([chunk])
        graph.add_graph_documents(graph_document)
        create_source_chunk_entity_relationship(file_name,graph,graph_document,chunk,isEmbedding,uri,userName,password)
        graph_document_list.append(graph_document[0]) 
           
    graph.refresh_schema()
    return graph_document_list
