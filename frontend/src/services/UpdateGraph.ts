import axios from 'axios';
import { url } from '../utils/Utils';

const updateGraphAPI = async (userCredentials: any) => {
  try {
    const formData = new FormData();
    formData.append('uri', userCredentials?.uri ?? '');
    formData.append('database', userCredentials?.database ?? '');
    formData.append('userName', userCredentials?.userName ?? '');
    formData.append('password', userCredentials?.password ?? '');
    const response: any = await axios.post(`${url()}/update_similarity_graph`, userCredentials, {
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

export { updateGraphAPI };
