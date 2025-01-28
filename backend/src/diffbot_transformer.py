from langchain_experimental.graph_transformers.diffbot import DiffbotGraphTransformer
from langchain_community.graphs import Neo4jGraph
from langchain.docstore.document import Document
from typing import List
import os


def extract_graph_from_diffbot(graph: Neo4jGraph, 
                               chunks: List[Document]):
    """ Create knowledge graph using diffbot transformer

    Args:
        graph (Neo4jGraph): Neo4jGraph connection object
        chunks (List[Document]): list of chunk documents created from input file

    Returns: langchain GraphDocument - used to generate graph
        
    """    
    diffbot_api_key = os.environ.get('DIFFBOT_API_KEY')
    diffbot_nlp = DiffbotGraphTransformer(diffbot_api_key=diffbot_api_key)
    graph_document_list = []
    
    for chunk in chunks:
        graph_document = diffbot_nlp.convert_to_graph_documents([chunk])
        graph.add_graph_documents(graph_document)
        graph_document_list.append(graph_document[0]) 
           
    graph.refresh_schema()
    return graph_document_list
    