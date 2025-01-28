import { Method } from 'axios';
import { url } from './Utils';
import { UserCredentials, ExtractParams, UploadParams } from '../types';
import { apiCall } from '../services/CommonAPI';

// Upload Call
export const uploadAPI = async (file: any, userCredentials: any, model: string): Promise<any> => {
  const urlUpload = `${url()}/sources`;
  const method: Method = 'post';
  const commonParams: UserCredentials = userCredentials;
  const additionalParams: UploadParams = { file, model };
  const response = await apiCall(urlUpload, method, commonParams, additionalParams);
  return response;
};

// Extract call
export const extractAPI = async (
  file: any,
  model: string,
  userCredentials: any,
  source_type: string,
  source_url?: any,
  aws_access_key_id?: any,
  aws_secret_access_key?: any,
  file_name?: string,
  gcs_bucket_name?: string,
  gcs_bucket_folder?: string
): Promise<any> => {
  const urlExtract = `${url()}/extract`;
  const method: Method = 'post';
  const commonParams: UserCredentials = userCredentials;
  let additionalParams: ExtractParams;
  if (source_type === 's3 bucket') {
    additionalParams = { model, source_url, aws_secret_access_key, aws_access_key_id };
  } else if (source_type === 'Wikipedia') {
    additionalParams = { model, wiki_query: file_name };
  } else if (source_type === 'gcs bucket') {
    additionalParams = { model, gcs_blob_filename: file_name, gcs_bucket_folder, gcs_bucket_name };
  } else if (source_type === 'youtube') {
    additionalParams = { model, source_url };
  } else {
    additionalParams = { model, file };
  }
  const response = await apiCall(urlExtract, method, commonParams, additionalParams);
  return response;
};
