import axios, { AxiosResponse } from 'axios';
import { url } from '../utils/Utils';
interface fileName {
  fileName: string;
  fileSize: number;
  url: string;
  gcsBucket?: string;
  gcsBucketFolder?: string;
}
interface URLSCAN_RESPONSE {
  status: string;
  success_count?: number;
  Failed_count?: number;
  message: string;
  file_name?: fileName[];
  error?: string;
  file_source?: string;
  data?: any;
}

interface ServerResponse extends Partial<AxiosResponse> {
  data: URLSCAN_RESPONSE;
}
interface ScanProps {
  urlParam?: string;
  userCredentials?: any;
  model?: string;
  accessKey?: string;
  secretKey?: string;
  wikiquery?: string;
  gcs_bucket_name?: string;
  gcs_bucket_folder?: string;
}

const urlScanAPI = async (props: ScanProps) => {
  try {
    const formData = new FormData();
    formData.append('uri', props?.userCredentials?.uri ?? '');
    formData.append('database', props?.userCredentials?.database ?? '');
    formData.append('userName', props?.userCredentials?.userName ?? '');
    formData.append('password', props?.userCredentials?.password ?? '');
    formData.append('source_url', props?.urlParam ?? '');
    formData.append('wiki_query', props?.wikiquery ?? '');
    if (props.model != undefined) {
      formData.append('model', props?.model);
    }
    if (props.accessKey?.length) {
      formData.append('aws_access_key_id', props?.accessKey);
    }
    if (props?.secretKey?.length) {
      formData.append('aws_secret_access_key', props?.secretKey);
    }
    if (props?.gcs_bucket_name) {
      formData.append('gcs_bucket_name', props.gcs_bucket_name);
    }
    if (props?.gcs_bucket_folder) {
      formData.append('gcs_bucket_folder', props.gcs_bucket_folder);
    }

    const response: ServerResponse = await axios.post(`${url()}/url/scan`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response;
  } catch (error) {
    console.log('Error uploading file:', error);
    throw error;
  }
};

export { urlScanAPI };
