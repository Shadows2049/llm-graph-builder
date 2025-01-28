from langchain_community.document_loaders import PyPDFLoader
from langchain_community.graphs import Neo4jGraph
from langchain.docstore.document import Document
from dotenv import load_dotenv
from datetime import datetime
import logging
from langchain.text_splitter import TokenTextSplitter
from tqdm import tqdm
from src.diffbot_transformer import extract_graph_from_diffbot
from src.openAI_llm import extract_graph_from_OpenAI
from typing import List
from langchain.document_loaders import S3DirectoryLoader
import boto3
from urllib.parse import urlparse
import os
import re
from tempfile import NamedTemporaryFile
import re
from langchain_community.document_loaders import YoutubeLoader

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(message)s',level='INFO')
# from langchain.document_loaders import S3FileLoader

def update_exception_db(graph_obj,file_name,exp_msg):
    job_status = "Failed"
    source_node = "fileName: '{}'"
    update_node_prop = 'SET d.status = "{}", d.errorMessage = "{}"'
    graph_obj.query('MERGE(d:Document {'+source_node.format(file_name)+'}) '+update_node_prop.format(job_status,exp_msg))

def create_source_node(graph_obj,file_name,file_size,file_type,source,model,url=None,aws_access_key_id=None):
  try:   
    current_time = datetime.now()
    job_status = "New"
    source_node = "fileName: '{}'"
    update_node_prop = "SET d.fileSize = '{}', d.fileType = '{}' ,d.status = '{}',d.url='{}',d.awsAccessKeyId='{}',d.fileSource='{}', d.createdAt ='{}', d.updatedAt = '{}', d.processingTime = '{}', d.errorMessage = '{}', d.nodeCount= {}, d.relationshipCount = {}, d.model= '{}'"
    logging.info("create source node as file name if not exist")
    graph_obj.query('MERGE(d:Document {'+source_node.format(file_name)+'}) '+update_node_prop.format(file_size,file_type,job_status,url,aws_access_key_id,source,current_time,current_time,0,'',0,0,model))
  except Exception as e:
    # job_status = "Failed"
    error_message = str(e)
    update_exception_db(graph_obj,file_name,error_message)
    # update_node_prop = 'SET d.status = "{}", d.errorMessage = "{}"'
    # graph_obj.query('MERGE(d:Document {'+source_node.format(file_name.split('/')[-1])+'}) '+update_node_prop.format(job_status,error_message))
    raise Exception(str(e))

def create_source_node_graph_local_file(uri, userName, password, file, model):
  """
   Creates a source node in Neo4jGraph and sets properties.
   
   Args:
   	 uri: URI of Graph Service to connect to
   	 userName: Username to connect to Graph Service with ( default : None )
   	 password: Password to connect to Graph Service with ( default : None )
   	 file: File object with information about file to be added
   
   Returns: 
   	 Success or Failed message of node creation
  """
  try:
    file_type = file.filename.split('.')[1]
    file_size = file.size
    file_name = file.filename
    source = 'local file'
    graph = Neo4jGraph(url=uri, username=userName, password=password)    

    create_source_node(graph,file_name,file_size,file_type,source,model)
    return create_api_response("Success",data="Source Node created successfully",file_source=source)
  except Exception as e:
    job_status = "Failed"
    error_message = str(e)
    return create_api_response(job_status,error=error_message,file_source=source)


def get_s3_files_info(s3_url,aws_access_key_id=None,aws_secret_access_key=None):
  # try:
      # Extract bucket name and directory from the S3 URL
      parsed_url = urlparse(s3_url)
      bucket_name = parsed_url.netloc
      directory = parsed_url.path.lstrip('/')
      try:
        # Connect to S3
        s3 = boto3.client('s3',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)

        # List objects in the specified directory
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=directory)
      except Exception as e:
         return {
    "status": "Failed",
    # "success_count": 0,
    # "Failed_count": 0,
    "message": "Invalid AWS credentials"}
      files_info = []

      # Check each object for file size and type
      for obj in response.get('Contents', []):
          file_key = obj['Key']
          file_name = os.path.basename(file_key)
          # file_name=s3_url.split('/')[-1]
          logging.info(f'file_name : {file_name}  and file key : {file_key}')
          file_size = obj['Size']

          # Check if file is a PDF
          if file_name.endswith('.pdf'):
            files_info.append({'file_key': file_key, 'file_size_bytes': file_size})
            
      return files_info  

def check_url_source(url):
    try:
      youtube_id_regex = re.search(r"v=([a-zA-Z0-9_-]+)", url)
        
      if url.startswith('s3://'):
        source ='s3 bucket'
        
      elif url.startswith("https://www.youtube.com/watch?") and youtube_id_regex is not None:
        if len(youtube_id_regex.group(1)) == 11:
            source = 'youtube'
            #re.match('^(https?:\/\/)?(www\.|m\.)?youtube\.com\/(c\/[^\/\?]+\/|channel\/[^\/\?]+\/|user\/[^\/\?]+\/)?(watch\?v=[^&\s]+|embed\/[^\/\?]+|[^\/\?]+)(&[^?\s]*)?$',url) :
        else :
          source = 'Invalid'
      else:
        source = 'Invalid'
      
      return source
    except Exception as e:
        raise e
  
def create_source_node_graph_url(uri, userName, password, source_url, max_limit, query_source, model, aws_access_key_id=None,aws_secret_access_key=None):
    """
      Creates a source node in Neo4jGraph and sets properties.
      
      Args:
        uri: URI of Graph Service to connect to
        userName: Username to connect to Graph Service with ( default : None )
        password: Password to connect to Graph Service with ( default : None )
        s3_url: s3 url for the bucket to fetch pdf files from
        aws_access_key_id: Aws access key id credentials (default : None)
        aws_secret_access_key: Aws secret access key credentials (default : None)
      Returns: 
        Success or Failed message of node creation
    """
    try:
        # if aws_access_key_id !=None and aws_secret_access_key !=None:
        #   os.environ['AWS_ACCESS_KEY_ID']=  aws_access_key_id
        #   os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_access_key
        graph = Neo4jGraph(url=uri, username=userName, password=password)
        source_type = check_url_source(source_url)
        print(f"source type URL:{source_type}")
        if source_type == "s3 bucket":
            files_info = get_s3_files_info(source_url,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
            if isinstance(files_info,dict):
              return files_info
            elif len(files_info)==0:
              return create_api_response('Failed',success_count=0,Failed_count=0,message='No pdf files found.')  
            logging.info(f'files info : {files_info}')
            err_flag=0
            success_count=0
            Failed_count=0
            file_type='pdf'
            for file_info in files_info:
                job_status = "New"
                file_name=file_info['file_key'] 
                file_size=file_info['file_size_bytes']
                s3_file_path=str(source_url+file_name)
                try:
                  create_source_node(graph,file_name,file_size,file_type,source_type,model,s3_file_path,aws_access_key_id)
                  success_count+=1
                except Exception as e:
                  err_flag=1
                  Failed_count+=1
                  error_message = str(e)
            if err_flag==1:
              job_status = "Failed"
              return create_api_response(job_status,error=error_message,success_count=success_count,Failed_count=Failed_count,file_source='s3 bucket')  
            return create_api_response("Success",data="Source Node created successfully",success_count=success_count,Failed_count=Failed_count,file_source='s3 bucket')
        elif source_type == 'youtube':
            match = re.search(r"v=([a-zA-Z0-9_-]+)", source_url)
            youtube_id=match.group(1)
            file_name=youtube_id
            file_size=''
            file_type='text'
            aws_access_key_id=''
            job_status = "Completed"
            create_source_node(graph,file_name,file_size,file_type,source_type,model,source_url,aws_access_key_id)
            return create_api_response(job_status)
        else:
           job_status = "Completed"
           return create_api_response(job_status,data='Unknown URL')
    except Exception as e:
        job_status = "Failed"
        error_message = str(e)
        logging.exception(f'Exception Stack trace:')
        return create_api_response(job_status,error=error_message,file_source=source_type)  
      
def file_into_chunks(pages: List[Document]):
    """
     Split a list of documents(file pages) into chunks of fixed size.
     
     Args:
     	 pages: A list of pages to split. Each page is a list of text strings.
     
     Returns: 
     	 A list of chunks each of which is a langchain Document.
    """
    logging.info("Split file into smaller chunks")
    text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=20)
    chunks = text_splitter.split_documents(pages)
    return chunks

def get_s3_pdf_content(s3_url,aws_access_key_id=None,aws_secret_access_key=None):
    # try:
      # Extract bucket name and directory from the S3 URL
        parsed_url = urlparse(s3_url)
        bucket_name = parsed_url.netloc
        logging.info(f'bucket name : {bucket_name}')
        directory = parsed_url.path.lstrip('/')
        if directory.endswith('.pdf'):
          loader=S3DirectoryLoader(bucket_name, prefix=directory,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
          pages = loader.load_and_split()
          return pages
        else:
          return None
    
    # except Exception as e:
    #     return None

def extract_graph_from_file(uri, userName, password, model, file=None,source_url=None,aws_access_key_id=None,aws_secret_access_key=None):
  """
   Extracts a Neo4jGraph from a PDF file based on the model.
   
   Args:
   	 uri: URI of the graph to extract
   	 userName: Username to use for graph creation ( if None will use username from config file )
   	 password: Password to use for graph creation ( if None will use password from config file )
   	 file: File object containing the PDF file to be used
   	 model: Type of model to use ('Diffbot'or'OpenAI GPT')
   
   Returns: 
   	 Json response to API with fileName, nodeCount, relationshipCount, processingTime, 
     status and model as attributes.
  """
  # logging.info(f"extract_graph_from_file called for file:{file.filename}")
  try:
    start_time = datetime.now()
    graph = Neo4jGraph(url=uri, username=userName, password=password)
    source_node = "fileName: '{}'" 
    if file!=None:
      file_name, file_key, pages = get_documents_from_file(file)
      
    elif check_url_source(source_url)=='s3 bucket':
      if(aws_access_key_id==None or aws_secret_access_key==None):
        job_status = "Failed"
        return create_api_response(job_status,error='Please provide AWS access and secret keys')
      else:
        file_name, file_key, pages = get_documents_from_s3(source_url, aws_access_key_id, aws_secret_access_key)
    
    elif check_url_source(source_url)=='youtube':
        file_name, file_key, pages = get_documents_from_youtube(source_url)
    
    else:
        job_status = "Failed"
        return create_api_response(job_status,error='Invalid url to create graph')
        
    if pages==None:
        job_status = "Failed"
        return create_api_response(job_status,error='Failed to load the pdf content')
        
    update_node_prop = "SET d.createdAt ='{}', d.updatedAt = '{}', d.processingTime = '{}',d.status = '{}', d.errorMessage = '{}',d.nodeCount= {}, d.relationshipCount = {}, d.model = '{}'"
    # pages = loader.load_and_split()
    bad_chars = ['"', "\n", "'"]
    for i in range(0,len(pages)):
      text = pages[i].page_content
      for j in bad_chars:
        if j == '\n':
          text = text.replace(j, ' ')
        else:
          text = text.replace(j, '')
      pages[i]=Document(page_content=str(text))
    logging.info("Break down file into chunks")
    chunks = file_into_chunks(pages)
    
    logging.info("Get graph document list from models")
    if model == 'Diffbot' :
      graph_documents = extract_graph_from_diffbot(graph,chunks,file_name,uri,userName,password)
      
    elif model == 'OpenAI GPT 3.5':
      model_version = 'gpt-3.5-turbo-16k'
      graph_documents = extract_graph_from_OpenAI(model_version,graph,chunks,file_name,uri,userName,password)
      
    elif model == 'OpenAI GPT 4':
      model_version = 'gpt-4-0125-preview' 
      graph_documents = extract_graph_from_OpenAI(model_version,graph,chunks,file_name,uri,userName,password)
              
    #update_similarity_graph for the KNN Graph
    update_graph()

    distinct_nodes = set()
    relations = []
    
    for graph_document in graph_documents:
      #get distinct nodes
      for node in graph_document.nodes:
            distinct_nodes.add(node.id)
      #get all relations
      for relation in graph_document.relationships:
            relations.append(relation.type)
      
    nodes_created = len(distinct_nodes)
    relationships_created = len(relations)  
    
    end_time = datetime.now()
    processed_time = end_time - start_time
    job_status = "Completed"
    error_message =""
    logging.info("Update source node properties")
    graph.query('MERGE(d:Document {'+source_node.format(file_key.split('/')[-1])+'}) '+update_node_prop.format(start_time,end_time,round(processed_time.total_seconds(),2),job_status,error_message,nodes_created,relationships_created,model))

    output = {
        "fileName": file_name,
        "nodeCount": nodes_created,
        "relationshipCount": relationships_created,
        "processingTime": round(processed_time.total_seconds(),2),
        "status" : job_status,
        "model" : model
    }
    logging.info(f'Response from extract API : {output}')
    return create_api_response("Success",data=output)
      
  except Exception as e:
      # job_status = "Failed"
      error_message = str(e)
      # update_node_prop = 'SET d.status = "{}", d.errorMessage = "{}"'
      update_exception_db(graph,file_name,error_message)
      # graph.query('MERGE(d:Document {'+source_node.format(file_name)+'}) '+update_node_prop.format(job_status,error_message))
      logging.exception(f'Exception Stack trace: {error_message}')
      return create_api_response(job_status,error=error_message)
  
def get_documents_from_file(file):
    print("get_documents_from_file called")
    file_name = file.filename
    print("file_name = ",file_name)
    file_key=file_name
    print("file_key = ",file_key)
        
    with open('temp.pdf','wb') as f:
        f.write(file.file.read())
    loader = PyPDFLoader('temp.pdf')
    pages = loader.load_and_split()
    return file_name,file_key,pages
    
def get_documents_from_s3(s3_url, aws_access_key_id, aws_secret_access_key):
    # if aws_access_key_id !=None and aws_secret_access_key !=None:
        #   os.environ['AWS_ACCESS_KEY_ID']=  aws_access_key_id
        #   os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_access_key
        
        parsed_url = urlparse(s3_url)
        bucket = parsed_url.netloc
        file_key = parsed_url.path.lstrip('/')
        file_name=file_key.split('/')[-1]
        s3=boto3.client('s3',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
        response=s3.head_object(Bucket=bucket,Key=file_key)
        # response = s3.get_object(Bucket=bucket, Key=file_key)
        file_size=response['ContentLength']
        
        logging.info(f'bucket : {bucket},  file key : {file_key},  file size : {file_size}')
        
        # loader = S3FileLoader(bucket,file_key)
        pages=get_s3_pdf_content(s3_url,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
        return file_name,file_key,pages
 
 
def get_documents_from_youtube(url):
          youtube_loader = YoutubeLoader.from_youtube_url(url, add_video_info=False)
          pages = youtube_loader.load()
          match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
          youtube_id=match.group(1)
          file_name=youtube_id
          file_key=file_name
          print("Youtube pages = ",pages)
          return file_name, file_key, pages     

def get_source_list_from_graph():
  """
   Returns a list of sources that are in the database by querying the graph and 
   sorting the list by the last updated date. 
 """
  logging.info("Get existing files list from graph")
  try:
    graph = Neo4jGraph()
    query = "MATCH(d:Document) RETURN d ORDER BY d.updatedAt DESC"
    result = graph.query(query)
    list_of_json_objects = [entry['d'] for entry in result]
    return create_api_response("Success",data=list_of_json_objects)
  except Exception as e:
    job_status = "Failed"
    error_message = str(e)
    logging.exception('Exception')
    return create_api_response(job_status,error=error_message)

def update_graph():
  """
  Update the graph node with SIMILAR relationship where embedding scrore match
  """
  knn_min_score = os.environ.get('KNN_MIN_SCORE')

  query = "WHERE node <> c and score >= {} MERGE (c)-[rel:SIMILAR]-(node) SET rel.score = score"
  graph = Neo4jGraph()
  result = graph.query("""MATCH (c:Chunk)
              WHERE c.embedding IS NOT NULL AND count { (c)-[:SIMILAR]-() } < 5
              CALL db.index.vector.queryNodes('vector', 6, c.embedding) yield node, score """+ query.format(knn_min_score))
  logging.info(f"result : {result}")
  return create_api_response("Success",message="Query executed successfully",data=result)

def create_api_response(status,success_count=None,Failed_count=None, data=None, error=None,message=None,file_source=None):
  """
   Create a response to be sent to the API. This is a helper function to create a JSON response that can be sent to the API.
   
   Args:
      status: The status of the API call. Should be one of the constants in this module.
      data: The data that was returned by the API call.
      error: The error that was returned by the API call.
      success_count: Number of files successfully processed.
      Failed_count: Number of files failed to process.
   Returns: 
   	 A dictionary containing the status data and error if any
  """
  response = {"status": status}

  # Set the data of the response
  if data is not None:
    response["data"] = data

  # Set the error message to the response.
  if error is not None:
    response["error"] = error
  
  if success_count is not None:
    response['success_count']=success_count
    response['Failed_count']=Failed_count
  
  if message is not None:
    response['message']=message

  if file_source is not None:
    response['file_source']=file_source
    
  return response