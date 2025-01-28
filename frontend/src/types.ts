import { Dispatch, SetStateAction } from 'react';
export interface CustomFile extends Partial<globalThis.File> {
  processing: string;
  status: string;
  NodesCount: number;
  id: string;
  relationshipCount: number;
  model: string;
}

export interface OptionType {
  value: string;
  label: string;
}
export type UserCredentials = {
  uri: string;
  userName: string;
  password: string;
};

export type ExtractParams = {
  file: string;
  model: string;
};
export type UploadParams = {
  file: string;
};

export type FormDataParams = ExtractParams | UploadParams;
export interface DropdownProps {
  onSelect: (option: OptionType | null | void) => void;
  isDisabled: boolean;
}
export interface CustomAlertProps {
  open: boolean;
  handleClose: () => void;
  alertMessage: string;
}
export interface S3ButtonProps {
  openModal: () => void;
}
export interface S3ModalProps {
  hideModal: () => void;
  open: boolean;
}
export interface ConnectionModalProps {
  open: boolean;
  setOpenConnection: Dispatch<SetStateAction<boolean>>;
  setConnectionStatus: Dispatch<SetStateAction<boolean>>;
}
export interface SourceNode {
  fileName: string;
  fileSize: number;
  fileType?: string;
  nodeCount?: number;
  processingTime?: string;
  relationshipCount?: number;
  model: string;
  status: string;
}
