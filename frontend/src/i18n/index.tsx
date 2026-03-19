import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

import type { AuthMethod, ProtocolOverride, TaskItem, TaskStatus } from '../api/types';
import type { TaskSocketStatus } from '../store/tasks';
import { formatBytes, formatSpeed, formatTimestamp } from '../utils/format';

export type AppLanguage = 'zh' | 'en';

type TranslationParamValue = string | number | boolean | null | undefined;
type TranslationParams = Record<string, TranslationParamValue>;
type MessageValue = string | ((params: TranslationParams) => string);

const LANGUAGE_STORAGE_KEY = 'sshferry.language';

const LANGUAGE_TO_LOCALE: Record<AppLanguage, string> = {
  zh: 'zh-CN',
  en: 'en-US',
};

const messages: Record<AppLanguage, Record<string, MessageValue>> = {
  zh: {
    'app.title': 'SSHFerry',
    'language.label': 'Language',
    'language.zh': 'ZH',
    'language.en': 'EN',
    'brand.frontend': 'SSHFerry Frontend',
    'nav.workspace': 'Workspace',
    'nav.tasks': 'Tasks',
    'nav.activity': 'Activity',
    'nav.debugLogs': 'Debug Logs',
    'nav.logs': 'Logs',
    'common.add': 'Add',
    'common.edit': 'Edit',
    'common.remove': 'Remove',
    'common.check': 'Check',
    'common.refresh': 'Refresh',
    'common.cancel': 'Cancel',
    'common.close': 'Close',
    'common.confirm': 'Confirm',
    'common.processing': 'Processing...',
    'common.save': 'Save',
    'common.saving': 'Saving...',
    'common.parse': 'Parse',
    'common.delete': 'Delete',
    'common.rename': 'Rename',
    'common.dismiss': 'Dismiss',
    'common.selectAll': 'Select All',
    'common.id': 'ID',
    'common.name': 'Name',
    'common.size': 'Size',
    'common.modified': 'Modified',
    'common.direction': 'Direction',
    'common.engine': 'Engine',
    'common.status': 'Status',
    'common.progress': 'Progress',
    'common.speed': 'Speed',
    'common.current': 'Current',
    'common.actions': 'Actions',
    'common.session': 'Session',
    'common.ready': 'Ready',
    'common.loading': 'Loading',
    'common.booting': 'Booting',
    'common.ok': 'OK',
    'common.fail': 'Fail',
    'common.loadingDirectory': 'Loading directory...',
    'common.directoryLoadFailed': 'Directory load failed',
    'common.viewFailureDetails': 'View failure details',
    'common.stale': 'Stale',
    'endpoint.local': 'Local',
    'endpoint.remote': 'Remote',
    'endpoint.workspace': 'Workspace',
    'protocol.auto': 'Auto',
    'auth.password': 'Password',
    'auth.key': 'Key',
    'auth.loginRequired': 'This deployed environment requires login before entering the workspace.',
    'auth.logout': 'Log Out',
    'auth.loggedOut': 'Logged out.',
    'auth.loginFailed': 'Login failed',
    'socket.idle': 'Idle',
    'socket.connecting': 'Connecting',
    'socket.connected': 'Connected',
    'socket.reconnecting': 'Reconnecting',
    'socket.polling': 'Polling',
    'socket.error': 'Error',
    'socket.pollFailed': 'Task polling failed',
    'socket.channelErrorTitle': 'Task channel returned an error',
    'socket.websocketError': 'Task WebSocket connection error',
    'socket.logPollFailed': 'Log polling failed',
    'socket.logChannelErrorTitle': 'Log channel returned an error',
    'socket.logWebsocketError': 'Log WebSocket connection error',
    'task.status.pending': 'Pending',
    'task.status.running': 'Running',
    'task.status.paused': 'Paused',
    'task.status.done': 'Done',
    'task.status.failed': 'Failed',
    'task.status.canceled': 'Canceled',
    'task.status.skipped': 'Skipped',
    'task.action.pause': 'Pause',
    'task.action.resume': 'Resume',
    'task.action.cancel': 'Cancel',
    'task.action.restart': 'Restart',
    'task.progress.folder': ({ done, total, progress, current }) =>
      `${done}/${total} files 鐠?${progress}%${current || ''}`,
    'task.progress.bytes': ({ progress, done, total }) => `${progress}% 鐠?${done}/${total}`,
    'task.progress.percent': ({ progress }) => `${progress}%`,
    'bootstrap.title': 'Preparing SSHFerry Workspace',
    'bootstrap.error': 'Initialization failed',
    'bootstrap.retry': 'Retry Initialization',
    'bootstrap.description': 'Checking backend health, restoring the login session, and preparing sites, sessions, and the task channel.',
    'bootstrap.complete': 'Ready',
    'bootstrap.connecting': 'Connecting...',
    'workspace.waitTitle': 'Waiting for Backend Initialization',
    'workspace.waitDescription': 'Preparing login state, sites, sessions, and the task channel.',
    'workspace.toast.noUploadSelection': 'No workspace selection available for upload',
    'workspace.toast.uploadSubmitted': 'Upload tasks submitted',
    'workspace.toast.downloadSubmitted': 'Download tasks submitted',
    'workspace.toast.remoteCopySubmitted': 'Remote copy tasks submitted',
    'workspace.toast.queueSummary': ({ successCount, total }) => `${successCount}/${total} items entered backend scheduling.`,
    'workspace.toast.noDownloadTarget': 'Missing download source or workspace target directory',
    'workspace.toast.noRemoteCopySelection': 'No remote selection available for copy',
    'workspace.toast.sessionClosed': 'Remote session closed',
    'workspace.middlePanelMode': 'Middle Panel',
    'workspace.middlePanelDescription': 'Switch between the upload workspace and an open remote session.',
    'workspace.middleSession': 'Displayed Session',
    'workspace.middleRemoteEmptyTitle': 'No remote session is available here',
    'workspace.middleRemoteEmptyBody': 'Open at least one remote session from the left, or switch back to the workspace panel.',
    'workspace.secondaryRemoteEmptyTitle': 'No additional remote sessions',
    'workspace.secondaryRemoteEmptyBody': 'One remote session is already pinned in the middle panel. Open another session to show it on the right.',
    'topbar.tagline': 'Multi-session file transfer workspace',
    'topbar.backend': 'Backend',
    'topbar.activityChannel': 'Activity WS',
    'topbar.protocol': 'Protocol',
    'topbar.language': 'Language',
    'topbar.user': 'User',
    'login.title': 'Log In to SSHFerry',
    'login.description': 'Use the initialized owner account to enter the deployed workspace. Public signup is disabled in Phase 1.',
    'login.username': 'Username',
    'login.password': 'Password',
    'login.usernamePlaceholder': 'Enter username',
    'login.passwordPlaceholder': 'Enter password',
    'login.submit': 'Log In',
    'login.submitting': 'Logging in...',
    'siteSidebar.title': 'Sites / Sessions',
    'siteSidebar.description': 'Primary control area for site management and global actions.',
    'siteSidebar.protocolOverride': 'Task Protocol Override',
    'siteSidebar.sites': 'Sites',
    'siteSidebar.selectedSite': 'Selected Site',
    'siteSidebar.openSessions': 'Open Sessions',
    'siteSidebar.connectionResult': 'Connection Result',
    'siteSidebar.authSummarySavedPassword': 'The backend already stored the password, so you can open a session directly.',
    'siteSidebar.authSummaryRuntimePassword': 'The password is not stored. Opening or checking will prompt for a runtime password.',
    'siteSidebar.authSummaryKey': 'Key-based authentication is enabled. The key path and advanced SSH options are saved in the site configuration.',
    'siteSidebar.toast.checkComplete': ({ siteName }) => `Connection check completed: ${siteName}`,
    'siteSidebar.toast.sessionOpened': 'Remote session opened',
    'siteSidebar.toast.sessionOpenedMessage': ({ siteName, sessionId }) => `${siteName} 鐠?${sessionId}`,
    'siteSidebar.toast.sessionClosed': 'Remote session closed',
    'siteSidebar.toast.siteDeleted': ({ siteName }) => `Site ${siteName} deleted`,
    'siteSidebar.confirm.closeSessionTitle': 'Close a session with related tasks',
    'siteSidebar.confirm.closeSessionDescription': ({ sessionId }) =>
      `Session ${sessionId} still has related tasks. Continuing will remove the current pane context.`,
    'siteSidebar.confirm.closeSession': 'Close Anyway',
    'siteSidebar.confirm.deleteSiteTitle': ({ siteName }) => `Delete site ${siteName}`,
    'siteSidebar.confirm.deleteSiteDescription': ({ siteName, count }) =>
      `This will delete site ${siteName} and close ${count} active sessions that reference it.`,
    'siteSidebar.confirm.deleteSite': 'Delete Site',
    'siteSidebar.connectionLine': ({ status, name, message }) => `${status} 鐠?${name} 鐠?${message}`,
    'siteSidebar.loadError': 'Failed to load the site sidebar',
    'siteSidebar.secretCheckTitle': 'Runtime Credentials: Connection Check',
    'siteSidebar.secretOpenTitle': 'Runtime Credentials: Open Session',
    'siteSidebar.secretCheckSubmit': 'Start Check',
    'siteSidebar.secretOpenSubmit': 'Open Session',
    'siteSidebar.closeSession': 'Close Session',
    'siteEditor.newTitle': 'New Site',
    'siteEditor.editTitle': 'Edit Site',
    'siteEditor.description': 'Aligned with backend fields and form semantics.',
    'siteEditor.quickImport': 'Quick Import from SSH Command',
    'siteEditor.siteName': 'Site Name',
    'siteEditor.host': 'Host',
    'siteEditor.port': 'Port',
    'siteEditor.username': 'Username',
    'siteEditor.remoteRoot': 'Remote Root',
    'siteEditor.defaultProtocol': 'Default Protocol',
    'siteEditor.authMethod': 'Auth Method',
    'siteEditor.password': 'Password',
    'siteEditor.rememberPassword': 'Remember Password',
    'siteEditor.keyPath': 'Key Path',
    'siteEditor.keyPassphrase': 'Key Passphrase',
    'siteEditor.advanced': 'Advanced',
    'siteEditor.proxyJump': 'Proxy Jump',
    'siteEditor.sshConfigPath': 'SSH Config Path',
    'siteEditor.sshOptions': 'SSH Options',
    'siteEditor.passwordPlaceholderSaved': 'Password already stored. Leave blank to keep it unchanged.',
    'siteEditor.passwordPlaceholderNew': 'Enter password',
    'siteEditor.keyPassphrasePlaceholderSaved': 'Key passphrase already stored. Leave blank to keep it unchanged.',
    'siteEditor.keyPassphrasePlaceholderNew': 'Enter a key passphrase if needed',
    'siteEditor.sshOptionsPlaceholder': 'One option per line, or separate them with commas',
    'siteEditor.parseError': 'Only the basic SSH command format is supported: ssh [-p PORT] [USER@]HOST',
    'siteEditor.toast.created': 'Site created',
    'siteEditor.toast.updated': 'Site updated',
    'siteEditor.toast.savedMessage': ({ siteName }) => `${siteName} has been added to the site list.`,
    'secret.runtimePassword': 'Runtime Password',
    'secret.keyPassphrase': 'Key Passphrase',
    'secret.runtimePasswordPlaceholder': 'Enter the password used for this connection',
    'secret.keyPassphrasePlaceholder': 'Leave blank if the key has no passphrase',
    'taskCenter.title': 'Task Center',
    'taskCenter.summary': ({ total, running, pending, failed, done }) =>
      `Total ${total} 鐠?Running ${running} 鐠?Pending ${pending} 鐠?Failed ${failed} 鐠?Done ${done}`,
    'taskCenter.clearFinished': 'Clear Finished',
    'taskCenter.toast.actionSubmitted': ({ action }) => `${action} requests submitted`,
    'taskCenter.toast.actionAccepted': ({ successCount, total }) => `${successCount}/${total} requests accepted.`,
    'taskCenter.toast.clearedFinished': 'Finished tasks cleared',
    'taskCenter.empty': 'No tasks right now.',
    'localPanel.title': 'Upload Workspace',
    'localPanel.description': 'Manage the deployed user workspace, upload files and folders, and receive remote downloads.',
    'localPanel.summary': ({ files, dirs, size }) => `${files} files 鐠?${dirs} directories 鐠?${size}`,
    'localPanel.pathPlaceholder': 'Enter a workspace path, for example /releases',
    'localPanel.empty': 'This directory is empty.',
    'localPanel.loadError': 'Unable to read the workspace directory',
    'localPanel.uploadFiles': 'Upload Files',
    'localPanel.uploadFolder': 'Upload Folder',
    'localPanel.deleteSelected': 'Delete Selected',
    'localPanel.deleteTitle': 'Delete Workspace Items',
    'localPanel.deleteDescription': 'The following workspace items will be deleted:\n{labels}',
    'localPanel.deleteConfirm': 'Confirm Delete',
    'localPanel.uploaded': 'Workspace upload completed',
    'localPanel.uploadedSummary': '{total} files uploaded into the workspace.',
    'localPanel.deleted': 'Workspace items deleted',
    'log.title': 'Raw Logs',
    'log.summary': ({ total }) => `Buffer ${total}`,
    'log.clear': 'Clear Logs',
    'log.cleared': 'Logs cleared',
    'log.autoScroll': 'Auto Scroll',
    'log.emptyTitle': 'No logs yet',
    'log.emptyBody': 'Wait for backend events, task scheduling, or connection activity to generate new log lines.',
    'log.backendRestartRequired': 'The current backend does not expose the deployed log channel yet, or the log capability is not wired in.',
    'remoteWorkspace.title': 'Remote Workspace',
    'remoteWorkspace.description': 'Side-by-side multi-session workspace.',
    'remoteWorkspace.emptyTitle': 'No remote sessions are open',
    'remoteWorkspace.emptyBody': 'Select a site on the left and open a session. Remote panes will be appended on the right in order.',
    'remotePane.deleteTitle': 'Delete Remote Path',
    'remotePane.deleteDescription': 'The following remote objects will be deleted:\n{labels}',
    'remotePane.deleteConfirm': 'Confirm Delete',
    'remotePane.deleteToast': 'Remote delete request submitted',
    'remotePane.closePane': 'Close Pane',
    'remotePane.staleTitle': 'Session Expired',
    'remotePane.staleBody': 'The backend restarted or the session no longer exists. Reopen the site from the left, or close this pane directly.',
    'remotePane.createDirectoryPrompt': 'Enter a new directory name',
    'remotePane.createDirectoryToast': 'Remote directory created',
    'remotePane.pathPlaceholder': 'Enter remote path',
    'remotePane.uploadLocalSelection': 'Upload Workspace Selection',
    'remotePane.downloadSelection': 'Download to Workspace',
    'remotePane.renamePrompt': 'Enter a new file or directory name',
    'remotePane.renameToast': 'Remote path renamed',
    'remotePane.empty': 'This remote directory is empty.',
    'remotePane.loadError': 'Unable to read the remote directory',
    'http.sessionInvalid': 'The current login session is invalid. Please log in again.',
    'http.sessionExpired': 'The login session has expired. Please log in again.',
    'http.backendNotReadyTitle': 'Backend Not Ready',
    'http.backendNotReadyMessage': 'The service is reachable, but its dependencies are not ready or required capabilities are missing on this machine.',
    'http.requestFailed': 'Request failed',
    'http.backendStartupIncomplete': 'The backend has not finished starting yet.',
    'http.initFailed': 'Initialization failed',
    'activity.title': 'Activity Feed',
    'activity.description': 'Recent auth, workspace, session, and task events for the current user.',
    'activity.pageDescription': 'Live activity stream for the current authenticated user.',
    'activity.summary': ({ total }) => `Events ${total}`,
    'activity.autoScroll': 'Auto Scroll',
    'activity.emptyTitle': 'No activity yet',
    'activity.emptyBody': 'Wait for auth, workspace, session, or task operations to generate new events.',
    'activity.backendRestartRequired':
      'The current backend does not expose the deployed activity feed yet, or the activity capability is not wired in.',
    'activity.pollFailed': 'Activity polling failed',
    'activity.channelErrorTitle': 'Activity channel returned an error',
    'activity.websocketError': 'Activity WebSocket connection error',
    'activity.category.auth': 'Auth',
    'activity.category.site': 'Site',
    'activity.category.session': 'Session',
    'activity.category.workspace': 'Workspace',
    'activity.category.remote': 'Remote',
    'activity.category.task': 'Task',
    'activity.category.system': 'System',
    'log.description': 'Owner-only backend log buffer for low-level diagnosis.',
    'log.pageDescription': 'Owner-only raw backend log stream for debugging and restart analysis.',  },
  en: {
    'app.title': 'SSHFerry',
    'language.label': 'Language',
    'language.zh': 'ZH',
    'language.en': 'EN',
    'brand.frontend': 'SSHFerry Frontend',
    'nav.workspace': 'Workspace',
    'nav.tasks': 'Tasks',
    'nav.activity': 'Activity',
    'nav.debugLogs': 'Debug Logs',
    'nav.logs': 'Logs',
    'common.add': 'Add',
    'common.edit': 'Edit',
    'common.remove': 'Remove',
    'common.check': 'Check',
    'common.refresh': 'Refresh',
    'common.cancel': 'Cancel',
    'common.close': 'Close',
    'common.confirm': 'Confirm',
    'common.processing': 'Processing...',
    'common.save': 'Save',
    'common.saving': 'Saving...',
    'common.parse': 'Parse',
    'common.delete': 'Delete',
    'common.rename': 'Rename',
    'common.dismiss': 'Dismiss',
    'common.selectAll': 'Select All',
    'common.id': 'ID',
    'common.name': 'Name',
    'common.size': 'Size',
    'common.modified': 'Modified',
    'common.direction': 'Direction',
    'common.engine': 'Engine',
    'common.status': 'Status',
    'common.progress': 'Progress',
    'common.speed': 'Speed',
    'common.current': 'Current',
    'common.actions': 'Actions',
    'common.session': 'Session',
    'common.ready': 'Ready',
    'common.loading': 'Loading',
    'common.booting': 'Booting',
    'common.ok': 'OK',
    'common.fail': 'Fail',
    'common.loadingDirectory': 'Loading directory...',
    'common.directoryLoadFailed': 'Directory load failed',
    'common.viewFailureDetails': 'View failure details',
    'common.stale': 'Stale',
    'endpoint.local': 'Local',
    'endpoint.remote': 'Remote',
    'endpoint.workspace': 'Workspace',
    'protocol.auto': 'Auto',
    'auth.password': 'Password',
    'auth.key': 'Key',
    'auth.loginRequired': 'This deployed environment requires login before entering the workspace.',
    'auth.logout': 'Log Out',
    'auth.loggedOut': 'Logged out.',
    'auth.loginFailed': 'Login failed',
    'socket.idle': 'Idle',
    'socket.connecting': 'Connecting',
    'socket.connected': 'Connected',
    'socket.reconnecting': 'Reconnecting',
    'socket.polling': 'Polling',
    'socket.error': 'Error',
    'socket.pollFailed': 'Task polling failed',
    'socket.channelErrorTitle': 'Task channel returned an error',
    'socket.websocketError': 'Task WebSocket connection error',
    'socket.logPollFailed': 'Log polling failed',
    'socket.logChannelErrorTitle': 'Log channel returned an error',
    'socket.logWebsocketError': 'Log WebSocket connection error',
    'task.status.pending': 'Pending',
    'task.status.running': 'Running',
    'task.status.paused': 'Paused',
    'task.status.done': 'Done',
    'task.status.failed': 'Failed',
    'task.status.canceled': 'Canceled',
    'task.status.skipped': 'Skipped',
    'task.action.pause': 'Pause',
    'task.action.resume': 'Resume',
    'task.action.cancel': 'Cancel',
    'task.action.restart': 'Restart',
    'task.progress.folder': ({ done, total, progress, current }) =>
      `${done}/${total} files 鐠?${progress}%${current || ''}`,
    'task.progress.bytes': ({ progress, done, total }) => `${progress}% 鐠?${done}/${total}`,
    'task.progress.percent': ({ progress }) => `${progress}%`,
    'bootstrap.title': 'Preparing SSHFerry Workspace',
    'bootstrap.error': 'Initialization failed',
    'bootstrap.retry': 'Retry Initialization',
    'bootstrap.description': 'Checking backend health, restoring the login session, and preparing sites, sessions, and the task channel.',
    'bootstrap.complete': 'Ready',
    'bootstrap.connecting': 'Connecting...',
    'workspace.waitTitle': 'Waiting for Backend Initialization',
    'workspace.waitDescription': 'Preparing login state, sites, sessions, and the task channel.',
    'workspace.toast.noUploadSelection': 'No workspace selection available for upload',
    'workspace.toast.uploadSubmitted': 'Upload tasks submitted',
    'workspace.toast.downloadSubmitted': 'Download tasks submitted',
    'workspace.toast.remoteCopySubmitted': 'Remote copy tasks submitted',
    'workspace.toast.queueSummary': ({ successCount, total }) => `${successCount}/${total} items entered backend scheduling.`,
    'workspace.toast.noDownloadTarget': 'Missing download source or workspace target directory',
    'workspace.toast.noRemoteCopySelection': 'No remote selection available for copy',
    'workspace.toast.sessionClosed': 'Remote session closed',
    'workspace.middlePanelMode': 'Middle Panel',
    'workspace.middlePanelDescription': 'Switch between the upload workspace and an open remote session.',
    'workspace.middleSession': 'Displayed Session',
    'workspace.middleRemoteEmptyTitle': 'No remote session is available here',
    'workspace.middleRemoteEmptyBody': 'Open at least one remote session from the left, or switch back to the workspace panel.',
    'workspace.secondaryRemoteEmptyTitle': 'No additional remote sessions',
    'workspace.secondaryRemoteEmptyBody': 'One remote session is already pinned in the middle panel. Open another session to show it on the right.',
    'topbar.tagline': 'Multi-session file transfer workspace',
    'topbar.backend': 'Backend',
    'topbar.activityChannel': 'Activity WS',
    'topbar.protocol': 'Protocol',
    'topbar.language': 'Language',
    'topbar.user': 'User',
    'login.title': 'Log In to SSHFerry',
    'login.description': 'Use the initialized owner account to enter the deployed workspace. Public signup is disabled in Phase 1.',
    'login.username': 'Username',
    'login.password': 'Password',
    'login.usernamePlaceholder': 'Enter username',
    'login.passwordPlaceholder': 'Enter password',
    'login.submit': 'Log In',
    'login.submitting': 'Logging in...',
    'siteSidebar.title': 'Sites / Sessions',
    'siteSidebar.description': 'Primary control area for site management and global actions.',
    'siteSidebar.protocolOverride': 'Task Protocol Override',
    'siteSidebar.sites': 'Sites',
    'siteSidebar.selectedSite': 'Selected Site',
    'siteSidebar.openSessions': 'Open Sessions',
    'siteSidebar.connectionResult': 'Connection Result',
    'siteSidebar.authSummarySavedPassword': 'The backend already stored the password, so you can open a session directly.',
    'siteSidebar.authSummaryRuntimePassword': 'The password is not stored. Opening or checking will prompt for a runtime password.',
    'siteSidebar.authSummaryKey': 'Key-based authentication is enabled. The key path and advanced SSH options are saved in the site configuration.',
    'siteSidebar.toast.checkComplete': ({ siteName }) => `Connection check completed: ${siteName}`,
    'siteSidebar.toast.sessionOpened': 'Remote session opened',
    'siteSidebar.toast.sessionOpenedMessage': ({ siteName, sessionId }) => `${siteName} 鐠?${sessionId}`,
    'siteSidebar.toast.sessionClosed': 'Remote session closed',
    'siteSidebar.toast.siteDeleted': ({ siteName }) => `Site ${siteName} deleted`,
    'siteSidebar.confirm.closeSessionTitle': 'Close a session with related tasks',
    'siteSidebar.confirm.closeSessionDescription': ({ sessionId }) =>
      `Session ${sessionId} still has related tasks. Continuing will remove the current pane context.`,
    'siteSidebar.confirm.closeSession': 'Close Anyway',
    'siteSidebar.confirm.deleteSiteTitle': ({ siteName }) => `Delete site ${siteName}`,
    'siteSidebar.confirm.deleteSiteDescription': ({ siteName, count }) =>
      `This will delete site ${siteName} and close ${count} active sessions that reference it.`,
    'siteSidebar.confirm.deleteSite': 'Delete Site',
    'siteSidebar.connectionLine': ({ status, name, message }) => `${status} 鐠?${name} 鐠?${message}`,
    'siteSidebar.loadError': 'Failed to load the site sidebar',
    'siteSidebar.secretCheckTitle': 'Runtime Credentials: Connection Check',
    'siteSidebar.secretOpenTitle': 'Runtime Credentials: Open Session',
    'siteSidebar.secretCheckSubmit': 'Start Check',
    'siteSidebar.secretOpenSubmit': 'Open Session',
    'siteSidebar.closeSession': 'Close Session',
    'siteEditor.newTitle': 'New Site',
    'siteEditor.editTitle': 'Edit Site',
    'siteEditor.description': 'Aligned with backend fields and form semantics.',
    'siteEditor.quickImport': 'Quick Import from SSH Command',
    'siteEditor.siteName': 'Site Name',
    'siteEditor.host': 'Host',
    'siteEditor.port': 'Port',
    'siteEditor.username': 'Username',
    'siteEditor.remoteRoot': 'Remote Root',
    'siteEditor.defaultProtocol': 'Default Protocol',
    'siteEditor.authMethod': 'Auth Method',
    'siteEditor.password': 'Password',
    'siteEditor.rememberPassword': 'Remember Password',
    'siteEditor.keyPath': 'Key Path',
    'siteEditor.keyPassphrase': 'Key Passphrase',
    'siteEditor.advanced': 'Advanced',
    'siteEditor.proxyJump': 'Proxy Jump',
    'siteEditor.sshConfigPath': 'SSH Config Path',
    'siteEditor.sshOptions': 'SSH Options',
    'siteEditor.passwordPlaceholderSaved': 'Password already stored. Leave blank to keep it unchanged.',
    'siteEditor.passwordPlaceholderNew': 'Enter password',
    'siteEditor.keyPassphrasePlaceholderSaved': 'Key passphrase already stored. Leave blank to keep it unchanged.',
    'siteEditor.keyPassphrasePlaceholderNew': 'Enter a key passphrase if needed',
    'siteEditor.sshOptionsPlaceholder': 'One option per line, or separate them with commas',
    'siteEditor.parseError': 'Only the basic SSH command format is supported: ssh [-p PORT] [USER@]HOST',
    'siteEditor.toast.created': 'Site created',
    'siteEditor.toast.updated': 'Site updated',
    'siteEditor.toast.savedMessage': ({ siteName }) => `${siteName} has been added to the site list.`,
    'secret.runtimePassword': 'Runtime Password',
    'secret.keyPassphrase': 'Key Passphrase',
    'secret.runtimePasswordPlaceholder': 'Enter the password used for this connection',
    'secret.keyPassphrasePlaceholder': 'Leave blank if the key has no passphrase',
    'taskCenter.title': 'Task Center',
    'taskCenter.summary': ({ total, running, pending, failed, done }) =>
      `Total ${total} 鐠?Running ${running} 鐠?Pending ${pending} 鐠?Failed ${failed} 鐠?Done ${done}`,
    'taskCenter.clearFinished': 'Clear Finished',
    'taskCenter.toast.actionSubmitted': ({ action }) => `${action} requests submitted`,
    'taskCenter.toast.actionAccepted': ({ successCount, total }) => `${successCount}/${total} requests accepted.`,
    'taskCenter.toast.clearedFinished': 'Finished tasks cleared',
    'taskCenter.empty': 'No tasks right now.',
    'localPanel.title': 'Upload Workspace',
    'localPanel.description': 'Manage the deployed user workspace, upload files and folders, and receive remote downloads.',
    'localPanel.summary': ({ files, dirs, size }) => `${files} files 鐠?${dirs} directories 鐠?${size}`,
    'localPanel.pathPlaceholder': 'Enter a workspace path, for example /releases',
    'localPanel.empty': 'This directory is empty.',
    'localPanel.loadError': 'Unable to read the workspace directory',
    'localPanel.uploadFiles': 'Upload Files',
    'localPanel.uploadFolder': 'Upload Folder',
    'localPanel.deleteSelected': 'Delete Selected',
    'localPanel.deleteTitle': 'Delete Workspace Items',
    'localPanel.deleteDescription': 'The following workspace items will be deleted:\n{labels}',
    'localPanel.deleteConfirm': 'Confirm Delete',
    'localPanel.uploaded': 'Workspace upload completed',
    'localPanel.uploadedSummary': '{total} files uploaded into the workspace.',
    'localPanel.deleted': 'Workspace items deleted',
    'log.title': 'Raw Logs',
    'log.summary': ({ total }) => `Buffer ${total}`,
    'log.clear': 'Clear Logs',
    'log.cleared': 'Logs cleared',
    'log.autoScroll': 'Auto Scroll',
    'log.emptyTitle': 'No logs yet',
    'log.emptyBody': 'Wait for backend events, task scheduling, or connection activity to generate new log lines.',
    'log.backendRestartRequired': 'The current backend does not expose the deployed log channel yet, or the log capability is not wired in.',
    'remoteWorkspace.title': 'Remote Workspace',
    'remoteWorkspace.description': 'Side-by-side multi-session workspace.',
    'remoteWorkspace.emptyTitle': 'No remote sessions are open',
    'remoteWorkspace.emptyBody': 'Select a site on the left and open a session. Remote panes will be appended on the right in order.',
    'remotePane.deleteTitle': 'Delete Remote Path',
    'remotePane.deleteDescription': 'The following remote objects will be deleted:\n{labels}',
    'remotePane.deleteConfirm': 'Confirm Delete',
    'remotePane.deleteToast': 'Remote delete request submitted',
    'remotePane.closePane': 'Close Pane',
    'remotePane.staleTitle': 'Session Expired',
    'remotePane.staleBody': 'The backend restarted or the session no longer exists. Reopen the site from the left, or close this pane directly.',
    'remotePane.createDirectoryPrompt': 'Enter a new directory name',
    'remotePane.createDirectoryToast': 'Remote directory created',
    'remotePane.pathPlaceholder': 'Enter remote path',
    'remotePane.uploadLocalSelection': 'Upload Workspace Selection',
    'remotePane.downloadSelection': 'Download to Workspace',
    'remotePane.renamePrompt': 'Enter a new file or directory name',
    'remotePane.renameToast': 'Remote path renamed',
    'remotePane.empty': 'This remote directory is empty.',
    'remotePane.loadError': 'Unable to read the remote directory',
    'http.sessionInvalid': 'The current login session is invalid. Please log in again.',
    'http.sessionExpired': 'The login session has expired. Please log in again.',
    'http.backendNotReadyTitle': 'Backend Not Ready',
    'http.backendNotReadyMessage': 'The service is reachable, but its dependencies are not ready or required capabilities are missing on this machine.',
    'http.requestFailed': 'Request failed',
    'http.backendStartupIncomplete': 'The backend has not finished starting yet.',
    'http.initFailed': 'Initialization failed',
    'activity.title': 'Activity Feed',
    'activity.description': 'Recent auth, workspace, session, and task events for the current user.',
    'activity.pageDescription': 'Live activity stream for the current authenticated user.',
    'activity.summary': ({ total }) => `Events ${total}`,
    'activity.autoScroll': 'Auto Scroll',
    'activity.emptyTitle': 'No activity yet',
    'activity.emptyBody': 'Wait for auth, workspace, session, or task operations to generate new events.',
    'activity.backendRestartRequired':
      'The current backend does not expose the deployed activity feed yet, or the activity capability is not wired in.',
    'activity.pollFailed': 'Activity polling failed',
    'activity.channelErrorTitle': 'Activity channel returned an error',
    'activity.websocketError': 'Activity WebSocket connection error',
    'activity.category.auth': 'Auth',
    'activity.category.site': 'Site',
    'activity.category.session': 'Session',
    'activity.category.workspace': 'Workspace',
    'activity.category.remote': 'Remote',
    'activity.category.task': 'Task',
    'activity.category.system': 'System',
    'log.description': 'Owner-only backend log buffer for low-level diagnosis.',
    'log.pageDescription': 'Owner-only raw backend log stream for debugging and restart analysis.',  },
};

const socketStatusKeys: Record<TaskSocketStatus, string> = {
  idle: 'socket.idle',
  connecting: 'socket.connecting',
  connected: 'socket.connected',
  reconnecting: 'socket.reconnecting',
  polling: 'socket.polling',
  error: 'socket.error',
};

const taskStatusKeys: Record<TaskStatus, string> = {
  pending: 'task.status.pending',
  running: 'task.status.running',
  paused: 'task.status.paused',
  done: 'task.status.done',
  failed: 'task.status.failed',
  canceled: 'task.status.canceled',
  skipped: 'task.status.skipped',
};

const authMethodKeys: Record<AuthMethod, string> = {
  password: 'auth.password',
  key: 'auth.key',
};

const endpointTypeKeys: Record<string, string> = {
  local: 'endpoint.local',
  remote: 'endpoint.remote',
  workspace: 'endpoint.workspace',
};

function isAppLanguage(value: string | null | undefined): value is AppLanguage {
  return value === 'zh' || value === 'en';
}

function detectInitialLanguage(): AppLanguage {
  if (typeof window !== 'undefined') {
    const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (isAppLanguage(stored)) {
      return stored;
    }
  }

  if (typeof navigator !== 'undefined') {
    return navigator.language.toLowerCase().startsWith('zh') ? 'zh' : 'en';
  }

  return 'en';
}

let currentLanguage: AppLanguage = detectInitialLanguage();

function replaceTemplate(message: string, params: TranslationParams): string {
  return message.replace(/\{(\w+)\}/g, (_, token: string) => String(params[token] ?? ''));
}

export function resolveLocale(language: AppLanguage = currentLanguage): string {
  return LANGUAGE_TO_LOCALE[language];
}

export function setCurrentLanguage(language: AppLanguage): void {
  currentLanguage = language;

  if (typeof window !== 'undefined') {
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
  }
  if (typeof document !== 'undefined') {
    document.documentElement.lang = resolveLocale(language);
    document.title = translate('app.title', {}, language);
  }
}

export function translate(key: string, params: TranslationParams = {}, language: AppLanguage = currentLanguage): string {
  const message = messages[language][key] ?? messages.en[key] ?? key;
  if (typeof message === 'function') {
    return message(params);
  }
  return replaceTemplate(message, params);
}

export function formatSocketStatusLabel(status: TaskSocketStatus, language: AppLanguage = currentLanguage): string {
  return translate(socketStatusKeys[status] ?? status, {}, language);
}

export function formatTaskStatusLabel(status: TaskStatus, language: AppLanguage = currentLanguage): string {
  return translate(taskStatusKeys[status] ?? status, {}, language);
}

export function formatProtocolLabel(
  protocol: ProtocolOverride | string,
  language: AppLanguage = currentLanguage,
): string {
  return protocol === 'auto' ? translate('protocol.auto', {}, language) : protocol.toUpperCase();
}

export function formatAuthMethodLabel(method: AuthMethod, language: AppLanguage = currentLanguage): string {
  return translate(authMethodKeys[method], {}, language);
}

export function formatEndpointTypeLabel(endpointType: string, language: AppLanguage = currentLanguage): string {
  const key = endpointTypeKeys[endpointType];
  return key ? translate(key, {}, language) : endpointType;
}

export function formatDirectionLabel(
  sourceType: string,
  targetType: string,
  language: AppLanguage = currentLanguage,
): string {
  return `${formatEndpointTypeLabel(sourceType, language)} -> ${formatEndpointTypeLabel(targetType, language)}`;
}

export function formatDateTimeLabel(
  value: number | null,
  language: AppLanguage = currentLanguage,
): string {
  return formatTimestamp(value, resolveLocale(language));
}

export function formatTaskProgressLabel(
  task: TaskItem,
  language: AppLanguage = currentLanguage,
): string {
  if (task.kind === 'folder_transfer' && task.subtask_count > 0) {
    const current = task.current_file ? ` 鐠?${task.current_file}` : '';
    return translate(
      'task.progress.folder',
      {
        done: task.subtask_done,
        total: task.subtask_count,
        progress: task.progress_percent.toFixed(1),
        current,
      },
      language,
    );
  }

  if (!task.bytes_total) {
    return translate('task.progress.percent', { progress: task.progress_percent.toFixed(1) }, language);
  }

  return translate(
    'task.progress.bytes',
    {
      progress: task.progress_percent.toFixed(1),
      done: formatBytes(task.bytes_done),
      total: formatBytes(task.bytes_total),
    },
    language,
  );
}

interface I18nContextValue {
  language: AppLanguage;
  locale: string;
  setLanguage: (language: AppLanguage) => void;
  t: (key: string, params?: TranslationParams) => string;
  formatDateTime: (value: number | null) => string;
  formatTaskProgress: (task: TaskItem) => string;
  formatTaskStatus: (status: TaskStatus) => string;
  formatSocketStatus: (status: TaskSocketStatus) => string;
  formatProtocol: (protocol: ProtocolOverride | string) => string;
  formatAuthMethod: (method: AuthMethod) => string;
  formatDirection: (sourceType: string, targetType: string) => string;
  formatEndpointType: (endpointType: string) => string;
  formatTransferSpeed: (value: number) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<AppLanguage>(() => detectInitialLanguage());

  useEffect(() => {
    setCurrentLanguage(language);
  }, [language]);

  return (
    <I18nContext.Provider
      value={{
        language,
        locale: resolveLocale(language),
        setLanguage,
        t: (key, params) => translate(key, params, language),
        formatDateTime: (value) => formatDateTimeLabel(value, language),
        formatTaskProgress: (task) => formatTaskProgressLabel(task, language),
        formatTaskStatus: (status) => formatTaskStatusLabel(status, language),
        formatSocketStatus: (status) => formatSocketStatusLabel(status, language),
        formatProtocol: (protocol) => formatProtocolLabel(protocol, language),
        formatAuthMethod: (method) => formatAuthMethodLabel(method, language),
        formatDirection: (sourceType, targetType) => formatDirectionLabel(sourceType, targetType, language),
        formatEndpointType: (endpointType) => formatEndpointTypeLabel(endpointType, language),
        formatTransferSpeed: (value) => formatSpeed(value),
      }}
    >
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n(): I18nContextValue {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within I18nProvider');
  }
  return context;
}