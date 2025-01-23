import Header from './Layout/Header';
import React from 'react';
import PageLayout from './Layout/PageLayout';
import { FileContextProvider } from '../context/UsersFiles';
import UserCredentialsWrapper from '../context/UserCredentials';
import AlertContextWrapper from '../context/Alert';
import { MessageContextWrapper } from '../context/UserMessages';
import { GraphContextWrapper } from '../context/GraphWrapper';

const QuickStarter: React.FunctionComponent = () => {
  return (
    <UserCredentialsWrapper>
      <FileContextProvider>
        <MessageContextWrapper>
          <GraphContextWrapper>
            <AlertContextWrapper>
              <Header />
              <PageLayout />
            </AlertContextWrapper>
          </GraphContextWrapper>
        </MessageContextWrapper>
      </FileContextProvider>
    </UserCredentialsWrapper>
  );
};
export default QuickStarter;
