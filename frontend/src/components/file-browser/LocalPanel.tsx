import { useEffect, useRef } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';

import { getErrorMessage } from '../../api/http';
import { deleteWorkspaceItems, listWorkspaceItems, statWorkspacePath, uploadWorkspaceFiles } from '../../api/workspace';
import type { TransferDragPayload } from '../../api/types';
import { useI18n } from '../../i18n';
import { useUiStore } from '../../store/ui';
import { useWorkspaceStore } from '../../store/workspace';
import { formatBytes } from '../../utils/format';
import { FileTable } from './FileTable';

interface LocalPanelProps {
  onQueueDownloads: (payload: TransferDragPayload, targetDir: string) => void | Promise<void>;
}

type BrowserFile = File & { webkitRelativePath?: string };

export function LocalPanel({ onQueueDownloads }: LocalPanelProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const folderInputRef = useRef<HTMLInputElement | null>(null);
  const uploadMenuRef = useRef<HTMLDetailsElement | null>(null);
  const localCurrentPath = useWorkspaceStore((state) => state.localCurrentPath);
  const localPathDraft = useWorkspaceStore((state) => state.localPathDraft);
  const localSelection = useWorkspaceStore((state) => state.localSelection);
  const setLocalPath = useWorkspaceStore((state) => state.setLocalPath);
  const setLocalPathDraft = useWorkspaceStore((state) => state.setLocalPathDraft);
  const setLocalSelection = useWorkspaceStore((state) => state.setLocalSelection);
  const toggleLocalSelection = useWorkspaceStore((state) => state.toggleLocalSelection);
  const openConfirm = useUiStore((state) => state.openConfirm);
  const pushToast = useUiStore((state) => state.pushToast);
  const { t } = useI18n();

  const currentPath = localCurrentPath || '/';

  const listingQuery = useQuery({
    queryKey: ['workspace-list', currentPath],
    queryFn: () => listWorkspaceItems(currentPath),
  });

  const statsQuery = useQuery({
    queryKey: ['workspace-stat', currentPath],
    queryFn: () => statWorkspacePath(currentPath),
  });

  const uploadMutation = useMutation({ mutationFn: uploadWorkspaceFiles });
  const deleteMutation = useMutation({ mutationFn: deleteWorkspaceItems });

  const selectedEntries = listingQuery.data?.items.filter((entry) => localSelection.includes(entry.path)) ?? [];
  const summary = statsQuery.data
    ? t('localPanel.summary', {
        files: statsQuery.data.file_count,
        dirs: statsQuery.data.dir_count,
        size: formatBytes(statsQuery.data.total_size),
      })
    : null;

  useEffect(() => {
    if (!listingQuery.data) {
      return;
    }
    if (listingQuery.data.current_path !== currentPath) {
      setLocalPath(listingQuery.data.current_path);
    }
  }, [currentPath, listingQuery.data, setLocalPath]);

  async function refreshWorkspace() {
    await Promise.all([listingQuery.refetch(), statsQuery.refetch()]);
  }

  function closeUploadMenu() {
    if (uploadMenuRef.current) {
      uploadMenuRef.current.open = false;
    }
  }

  async function handleUploadSelection(files: FileList | null) {
    const selectedFiles = Array.from(files ?? []);
    if (!selectedFiles.length) {
      return;
    }
    const relativePaths = selectedFiles.map((file) => {
      const browserFile = file as BrowserFile;
      return browserFile.webkitRelativePath && browserFile.webkitRelativePath.trim()
        ? browserFile.webkitRelativePath
        : file.name;
    });

    await uploadMutation.mutateAsync({
      targetPath: listingQuery.data?.current_path || currentPath,
      files: selectedFiles,
      relativePaths,
    });

    pushToast({
      tone: 'success',
      title: t('localPanel.uploaded'),
      message: t('localPanel.uploadedSummary', { total: selectedFiles.length }),
    });
    await refreshWorkspace();
  }

  function handleDelete() {
    if (!selectedEntries.length) {
      return;
    }
    const labels = selectedEntries.map((entry) => entry.path).join('\n');
    openConfirm({
      title: t('localPanel.deleteTitle'),
      description: t('localPanel.deleteDescription', { labels }),
      confirmLabel: t('localPanel.deleteConfirm'),
      destructive: true,
      onConfirm: async () => {
        await deleteMutation.mutateAsync(selectedEntries.map((entry) => entry.path));
        setLocalSelection([]);
        pushToast({ tone: 'success', title: t('localPanel.deleted') });
        await refreshWorkspace();
      },
    });
  }

  return (
    <section className="panel-shell local-panel">
      <header className="panel-header local-panel-header">
        <div className="local-panel-header-copy">
          <h3>{t('localPanel.title')}</h3>
          <p>{t('localPanel.description')}</p>
          {summary ? <p className="mono-cell">{summary}</p> : null}
        </div>
        <div className="local-panel-actions">
          <button
            type="button"
            className="ghost-button local-panel-nav-button"
            onClick={() => {
              if (listingQuery.data?.parent_path) {
                setLocalPath(listingQuery.data.parent_path);
              }
            }}
            disabled={!listingQuery.data?.parent_path}
          >
            ..
          </button>
          <details ref={uploadMenuRef} className="local-panel-upload-menu">
            <summary className="ghost-button local-panel-upload-trigger">{t('localPanel.uploadAction')}</summary>
            <div className="local-panel-upload-sheet">
              <button
                type="button"
                className="local-panel-upload-option"
                onClick={() => {
                  closeUploadMenu();
                  fileInputRef.current?.click();
                }}
              >
                {t('localPanel.uploadFiles')}
              </button>
              <button
                type="button"
                className="local-panel-upload-option"
                onClick={() => {
                  closeUploadMenu();
                  folderInputRef.current?.click();
                }}
              >
                {t('localPanel.uploadFolder')}
              </button>
            </div>
          </details>
          <button
            type="button"
            className="ghost-button danger-text"
            disabled={!selectedEntries.length}
            onClick={handleDelete}
          >
            {t('localPanel.deleteSelected')}
          </button>
        </div>
        <input
          ref={fileInputRef}
          hidden
          type="file"
          multiple
          onChange={(event) => {
            void handleUploadSelection(event.target.files);
            event.currentTarget.value = '';
          }}
        />
        <input
          ref={folderInputRef}
          hidden
          type="file"
          multiple
          {...({ webkitdirectory: '', directory: '' } as Record<string, string>)}
          onChange={(event) => {
            void handleUploadSelection(event.target.files);
            event.currentTarget.value = '';
          }}
        />
      </header>
      <div className="path-bar">
        <input
          value={localPathDraft}
          onChange={(event) => setLocalPathDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && localPathDraft.trim()) {
              setLocalPath(localPathDraft.trim());
            }
          }}
          placeholder={t('localPanel.pathPlaceholder')}
        />
      </div>
      <FileTable
        entries={listingQuery.data?.items ?? []}
        selectedPaths={localSelection}
        currentPath={listingQuery.data?.current_path || currentPath}
        emptyMessage={t('localPanel.empty')}
        isLoading={listingQuery.isPending}
        errorMessage={listingQuery.error ? getErrorMessage(listingQuery.error, t('localPanel.loadError')) : null}
        onSelect={(path, multi) => toggleLocalSelection(path, multi)}
        onActivate={(entry) => {
          if (entry.is_dir) {
            setLocalPath(entry.path);
          }
        }}
        dragPayloadFactory={(entry) => ({
          kind: 'local',
          paths: localSelection.includes(entry.path) ? localSelection : [entry.path],
        })}
        onDropTransfer={(payload, targetPath) => {
          if (payload.kind !== 'remote') {
            return;
          }
          void onQueueDownloads(payload, targetPath);
        }}
      />
    </section>
  );
}