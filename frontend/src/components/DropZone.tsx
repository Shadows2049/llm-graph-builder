import { Dropzone } from '@neo4j-ndl/react';
import React, { useState, useEffect, FunctionComponent } from 'react';
import Loader from '../utils/Loader';
import { v4 as uuidv4 } from 'uuid';
import { useCredentials } from '../context/UserCredentials';
import { useFileContext } from '../context/UsersFiles';
import { getFileFromLocal, saveFileToLocal } from '../utils/Utils';
import CustomAlert from './Alert';
import { uploadAPI } from '../utils/FileAPI';
import { CustomFile } from '../types';

const DropZone: FunctionComponent = () => {
  const { files, filesData, setFiles, setFilesData, model } = useFileContext();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isClicked, setIsClicked] = useState<boolean>(false);
  const { userCredentials } = useCredentials();
  const [errorMessage, setErrorMessage] = React.useState<string>('');
  const [showAlert, setShowAlert] = React.useState<boolean>(false);

  const onDropHandler = (f: Partial<globalThis.File>[]) => {
    setIsClicked(true);
    f.forEach((i) => saveFileToLocal(i));
    setIsLoading(false);
    if (f.length) {
      const defaultValues: CustomFile = {
        processing: 0,
        status: 'None',
        NodesCount: 0,
        id: uuidv4(),
        relationshipCount: 0,
        type: 'PDF',
        model: model,
        fileSource: 'local file',
      };

      const copiedFilesData: CustomFile[] = [...filesData];
      const copiedFiles: File[] = [...files];

      f.forEach((file) => {
        const filedataIndex = copiedFilesData.findIndex((filedataitem) => filedataitem?.name === file?.name);
        const fileIndex = copiedFiles.findIndex((filedataitem) => filedataitem?.name === file?.name);
        if (filedataIndex == -1) {
          copiedFilesData.unshift({
            name: file.name,
            type: file.type,
            size: file.size,
            ...defaultValues,
          });
        } else {
          const tempFileData = copiedFilesData[filedataIndex];
          copiedFilesData.splice(filedataIndex, 1);
          copiedFilesData.unshift({
            ...tempFileData,
            status: defaultValues.status,
            NodesCount: defaultValues.NodesCount,
            relationshipCount: defaultValues.relationshipCount,
            processing: defaultValues.processing,
            model: defaultValues.model,
            fileSource: defaultValues.fileSource,
          });
        }
        if (fileIndex == -1) {
          copiedFiles.unshift(file as File);
        } else {
          const tempFile = copiedFiles[filedataIndex];
          copiedFiles.splice(fileIndex, 1);
          copiedFiles.unshift(getFileFromLocal(tempFile.name) ?? tempFile);
        }
      });
      setFiles(copiedFiles);
      setFilesData(copiedFilesData);
    }
  };

  const fileUpload = async (file: File, uid: number) => {
    if (filesData[uid]?.status == 'None' && isClicked) {
      try {
        setIsLoading(true);
        setFilesData((prevfiles) =>
          prevfiles.map((curfile, idx) => {
            if (idx == uid) {
              return {
                ...curfile,
                status: 'Uploading',
              };
            }
            return curfile;
          })
        );
        const apiResponse = await uploadAPI(file, userCredentials, model);
        if (apiResponse?.status === 'Failed') {
          throw new Error(`message:${apiResponse.message},fileName:${apiResponse.file_name}`);
        } else {
          setFilesData((prevfiles) =>
            prevfiles.map((curfile) => {
              if (curfile.name === apiResponse?.file_name) {
                return {
                  ...curfile,
                  status: 'New',
                };
              }
              return curfile;
            })
          );
        }
        setIsClicked(false);
        setIsLoading(false);
      } catch (err: any) {
        const errorMessage = err.message;
        const messageMatch = errorMessage.match(/message:(.*),fileName:(.*)/);
        if (err?.name === 'AxiosError') {
          setShowAlert(true);
          setErrorMessage(err.message);
          setFilesData((prevfiles) =>
            prevfiles.map((curfile, idx) => {
              if (idx == uid) {
                return {
                  ...curfile,
                  status: 'Failed',
                };
              }
              return curfile;
            })
          );
        } else {
          const message = messageMatch[1].trim();
          const fileName = messageMatch[2].trim();
          setShowAlert(true);
          setErrorMessage(message);
          setFilesData((prevfiles) =>
            prevfiles.map((curfile) => {
              if (curfile.name == fileName) {
                return {
                  ...curfile,
                  status: 'Failed',
                  type: curfile.type?.split('/')[1]?.toUpperCase() ?? 'PDF',
                };
              }
              return curfile;
            })
          );
        }
      }
    }
  };
  const handleClose = () => {
    setShowAlert(false);
  };
  useEffect(() => {
    if (files.length > 0) {
      for (let i = 0; i < files.length; i++) {
        fileUpload(files[i], i);
      }
    }
  }, [files]);

  return (
    <>
      <CustomAlert open={showAlert} handleClose={handleClose} alertMessage={errorMessage} />
      <Dropzone
        loadingComponent={isLoading && <Loader />}
        isTesting={true}
        className='bg-none'
        dropZoneOptions={{
          accept: { 'application/pdf': ['.pdf'] },
          onDrop: (f: Partial<globalThis.File>[]) => {
            onDropHandler(f);
          },
          maxSize: 15000000,
          onDropRejected: (e) => {
            if (e.length) {
              setShowAlert(true);
              setErrorMessage(`Failed To Upload, File is larger than 15MB`);
            }
          },
        }}
      />
    </>
  );
};

export default DropZone;
