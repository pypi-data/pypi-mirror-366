import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { Contents } from '@jupyterlab/services';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ToolService } from './Services/ToolService';
import { NotebookTools } from './Notebook/NotebookTools';
import { NotebookContextManager } from './Notebook/NotebookContextManager';
import { PlanStateDisplay } from './Components/PlanStateDisplay';
import { WaitingUserReplyBoxManager } from './Notebook/WaitingUserReplyBoxManager';
import { ActionHistory } from './Chat/ActionHistory';
import { NotebookDiffManager } from './Notebook/NotebookDiffManager';
import { CellTrackingService } from './CellTrackingService';
import { TrackingIDUtility } from './TrackingIDUtility';
import { ContextCellHighlighter } from './Notebook/ContextCellHighlighter';
import { NotebookChatContainer } from './Notebook/NotebookChatContainer';
import { ListModel } from '@jupyterlab/extensionmanager';
import { IChatService } from './Services/IChatService';
import { IConfig } from './Config/ConfigService';
import { ServiceManager } from '@jupyterlab/services';

interface AppState {
  // Core services
  toolService: ToolService | null;
  notebookTracker: INotebookTracker | null;
  notebookTools: NotebookTools | null;
  notebookContextManager: NotebookContextManager | null;
  contentManager: Contents.IManager | null;
  settingsRegistry: ISettingRegistry | null;
  chatService: IChatService | null;
  config: IConfig | null;
  serviceManager: ServiceManager.IManager | null;

  // Extension manager
  extensions: ListModel | null;

  // Managers
  planStateDisplay: PlanStateDisplay | null;
  waitingUserReplyBoxManager: WaitingUserReplyBoxManager | null;
  notebookDiffManager: NotebookDiffManager | null;

  // Additional services
  actionHistory: ActionHistory | null;
  cellTrackingService: CellTrackingService | null;
  trackingIDUtility: TrackingIDUtility | null;
  contextCellHighlighter: ContextCellHighlighter | null;

  // UI Containers
  chatContainer: NotebookChatContainer | null;

  // Application state
  currentNotebookId: string | null;
  currentNotebook: NotebookPanel | null;
  isInitialized: boolean;

  // Settings
  settings: {
    theme: string;
    tokenMode: boolean;
    claudeApiKey: string;
    claudeModelId: string;
    claudeModelUrl: string;
    databaseUrl: string;
  };
}

const initialState: AppState = {
  // Core services
  toolService: null,
  notebookTracker: null,
  notebookTools: null,
  notebookContextManager: null,
  contentManager: null,
  settingsRegistry: null,
  chatService: null,
  config: null,
  serviceManager: null,

  // Extension manager
  extensions: null,

  // Managers
  planStateDisplay: null,
  waitingUserReplyBoxManager: null,
  notebookDiffManager: null,

  // Additional services
  actionHistory: null,
  cellTrackingService: null,
  trackingIDUtility: null,
  contextCellHighlighter: null,

  // UI Containers
  chatContainer: null,

  // Application state
  currentNotebookId: null,
  currentNotebook: null,
  isInitialized: false,

  // Settings
  settings: {
    theme: 'light',
    tokenMode: false,
    claudeApiKey: '',
    claudeModelId: 'claude-3-7-sonnet-20250219',
    claudeModelUrl: 'https://sage.alpinex.ai:8760',
    databaseUrl: ''
  }
};

const state$ = new BehaviorSubject<AppState>(initialState);

// Events for notebook changes
const notebookChanged$ = new Subject<{
  oldNotebookId: string | null;
  newNotebookId: string | null;
}>();
const notebookRenamed$ = new Subject<{
  oldNotebookId: string;
  newNotebookId: string;
}>();

export const AppStateService = {
  /**
   * Get the current application state
   */
  getState: () => state$.getValue(),

  /**
   * Update the application state with partial values
   */
  setState: (partial: Partial<AppState>) =>
    state$.next({ ...state$.getValue(), ...partial }),

  /**
   * Subscribe to state changes
   */
  changes: state$.asObservable(),

  /**
   * Initialize core services
   */
  initializeCoreServices: (
    toolService: ToolService,
    notebookTracker: INotebookTracker,
    notebookTools: NotebookTools,
    notebookContextManager: NotebookContextManager,
    contentManager: Contents.IManager,
    settingsRegistry?: ISettingRegistry | null
  ) => {
    AppStateService.setState({
      toolService,
      notebookTracker,
      notebookTools,
      notebookContextManager,
      contentManager,
      settingsRegistry: settingsRegistry || null
    });
  },

  /**
   * Initialize managers
   */
  initializeManagers: (
    planStateDisplay: PlanStateDisplay,
    waitingUserReplyBoxManager: WaitingUserReplyBoxManager,
    notebookDiffManager?: NotebookDiffManager
  ) => {
    AppStateService.setState({
      planStateDisplay,
      waitingUserReplyBoxManager,
      notebookDiffManager
    });
  },

  /**
   * Initialize additional services
   */
  initializeAdditionalServices: (
    actionHistory: ActionHistory,
    cellTrackingService: CellTrackingService,
    trackingIDUtility: TrackingIDUtility,
    contextCellHighlighter: ContextCellHighlighter
  ) => {
    AppStateService.setState({
      actionHistory,
      cellTrackingService,
      trackingIDUtility,
      contextCellHighlighter
    });
  },

  /**
   * Mark the application as initialized
   */
  markAsInitialized: () => {
    AppStateService.setState({ isInitialized: true });
  },

  /**
   * Get the current notebook ID
   */
  getCurrentNotebookId: (): string | null => {
    return AppStateService.getState().currentNotebookId;
  },

  /**
   * Get the current notebook
   */
  getCurrentNotebook: (): NotebookPanel | null => {
    return AppStateService.getState().currentNotebook;
  },

  /**
   * Set the current notebook and its ID
   */
  setCurrentNotebook: (
    notebook: NotebookPanel | null,
    notebookId?: string | null
  ) => {
    const currentState = AppStateService.getState();
    const oldNotebookId = currentState.currentNotebookId;
    const newNotebookId = notebookId || (notebook ? 'unknown' : null);

    if (oldNotebookId !== newNotebookId) {
      AppStateService.setState({
        currentNotebook: notebook,
        currentNotebookId: newNotebookId
      });
      // Emit notebook change event
      notebookChanged$.next({ oldNotebookId, newNotebookId });
    } else {
      // Just update the notebook reference if ID is the same
      AppStateService.setState({ currentNotebook: notebook });
    }
  },

  /**
   * Update the current notebook ID
   */
  setCurrentNotebookId: (notebookId: string | null) => {
    const currentState = AppStateService.getState();
    const oldNotebookId = currentState.currentNotebookId;

    if (oldNotebookId !== notebookId) {
      AppStateService.setState({
        currentNotebookId: notebookId,
        currentNotebook: null // Clear notebook reference when only ID is set
      });
      // Emit notebook change event
      notebookChanged$.next({ oldNotebookId, newNotebookId: notebookId });
    }
  },

  /**
   * Update notebook ID when a notebook is renamed
   */
  updateNotebookId: (oldNotebookId: string, newNotebookId: string) => {
    const currentState = AppStateService.getState();

    // Update current notebook ID if it matches the old one
    if (currentState.currentNotebookId === oldNotebookId) {
      AppStateService.setState({
        currentNotebookId: newNotebookId,
        currentNotebook: null // Clear notebook reference during rename
      });
    }

    // Emit notebook rename event
    notebookRenamed$.next({ oldNotebookId, newNotebookId });
  },

  /**
   * Subscribe to notebook change events
   */
  onNotebookChanged: (): Observable<{
    oldNotebookId: string | null;
    newNotebookId: string | null;
  }> => {
    return notebookChanged$.asObservable();
  },

  /**
   * Subscribe to notebook rename events
   */
  onNotebookRenamed: (): Observable<{
    oldNotebookId: string;
    newNotebookId: string;
  }> => {
    return notebookRenamed$.asObservable();
  },

  /**
   * Update settings
   */
  updateSettings: (settings: Partial<AppState['settings']>) => {
    const currentState = AppStateService.getState();
    AppStateService.setState({
      settings: { ...currentState.settings, ...settings }
    });
  },

  /**
   * Update Claude settings specifically
   */
  updateClaudeSettings: (settings: {
    claudeApiKey?: string;
    claudeModelId?: string;
    claudeModelUrl?: string;
    databaseUrl?: string;
  }) => {
    const currentState = AppStateService.getState();
    AppStateService.setState({
      settings: { ...currentState.settings, ...settings }
    });
  },

  /**
   * Get Claude settings
   */
  getClaudeSettings: (): {
    claudeApiKey: string;
    claudeModelId: string;
    claudeModelUrl: string;
    databaseUrl: string;
  } => {
    const { settings } = AppStateService.getState();
    return {
      claudeApiKey: settings.claudeApiKey,
      claudeModelId: settings.claudeModelId,
      claudeModelUrl: settings.claudeModelUrl,
      databaseUrl: settings.databaseUrl
    };
  },

  /**
   * Get Claude API key
   */
  getClaudeApiKey: (): string => {
    return AppStateService.getState().settings.claudeApiKey;
  },

  /**
   * Get Claude model URL
   */
  getClaudeModelUrl: (): string => {
    return AppStateService.getState().settings.claudeModelUrl;
  },

  /**
   * Get Claude model ID
   */
  getClaudeModelId: (): string => {
    return AppStateService.getState().settings.claudeModelId;
  },

  /**
   * Set the extensions manager
   */
  setExtensions: (extensions: ListModel) => {
    AppStateService.setState({ extensions });
  },

  /**
   * Get the extensions manager
   */
  getExtensions: (): ListModel | null => {
    return AppStateService.getState().extensions;
  },

  /**
   * Set the settings registry
   */
  setSettingsRegistry: (settingsRegistry: ISettingRegistry | null) => {
    AppStateService.setState({ settingsRegistry });
  },

  /**
   * Get the settings registry
   */
  getSettingsRegistry: (): ISettingRegistry | null => {
    return AppStateService.getState().settingsRegistry;
  },

  /**
   * Set the service manager
   */
  setServiceManager: (serviceManager: ServiceManager.IManager) => {
    AppStateService.setState({ serviceManager });
  },

  /**
   * Get the service manager
   */
  getServiceManager: (): ServiceManager.IManager | null => {
    return AppStateService.getState().serviceManager;
  },

  /**
   * Get a specific service safely
   */
  getToolService: (): ToolService => {
    const toolService = AppStateService.getState().toolService;
    if (!toolService) {
      throw new Error('ToolService not initialized in AppState');
    }
    return toolService;
  },

  getNotebookTracker: (): INotebookTracker => {
    const notebookTracker = AppStateService.getState().notebookTracker;
    if (!notebookTracker) {
      throw new Error('NotebookTracker not initialized in AppState');
    }
    return notebookTracker;
  },

  getNotebookTools: (): NotebookTools => {
    const notebookTools = AppStateService.getState().notebookTools;
    if (!notebookTools) {
      throw new Error('NotebookTools not initialized in AppState');
    }
    return notebookTools;
  },

  getNotebookContextManager: (): NotebookContextManager => {
    const notebookContextManager =
      AppStateService.getState().notebookContextManager;
    if (!notebookContextManager) {
      throw new Error('NotebookContextManager not initialized in AppState');
    }
    return notebookContextManager;
  },

  getContentManager: (): Contents.IManager => {
    const contentManager = AppStateService.getState().contentManager;
    if (!contentManager) {
      throw new Error('ContentManager not initialized in AppState');
    }
    return contentManager;
  },

  getPlanStateDisplay: (): PlanStateDisplay => {
    const planStateDisplay = AppStateService.getState().planStateDisplay;
    if (!planStateDisplay) {
      throw new Error('PlanStateDisplay not initialized in AppState');
    }
    return planStateDisplay;
  },

  getWaitingUserReplyBoxManager: (): WaitingUserReplyBoxManager => {
    const waitingUserReplyBoxManager =
      AppStateService.getState().waitingUserReplyBoxManager;
    if (!waitingUserReplyBoxManager) {
      throw new Error('WaitingUserReplyBoxManager not initialized in AppState');
    }
    return waitingUserReplyBoxManager;
  },

  getActionHistory: (): ActionHistory => {
    const actionHistory = AppStateService.getState().actionHistory;
    if (!actionHistory) {
      throw new Error('ActionHistory not initialized in AppState');
    }
    return actionHistory;
  },

  getCellTrackingService: (): CellTrackingService => {
    const cellTrackingService = AppStateService.getState().cellTrackingService;
    if (!cellTrackingService) {
      throw new Error('CellTrackingService not initialized in AppState');
    }
    return cellTrackingService;
  },

  getNotebookDiffManager: (): NotebookDiffManager => {
    const notebookDiffManager = AppStateService.getState().notebookDiffManager;
    if (!notebookDiffManager) {
      throw new Error('NotebookDiffManager not initialized in AppState');
    }
    return notebookDiffManager;
  },

  getTrackingIDUtility: (): TrackingIDUtility => {
    const trackingIDUtility = AppStateService.getState().trackingIDUtility;
    if (!trackingIDUtility) {
      throw new Error('TrackingIDUtility not initialized in AppState');
    }
    return trackingIDUtility;
  },

  getContextCellHighlighter: (): ContextCellHighlighter => {
    const contextCellHighlighter =
      AppStateService.getState().contextCellHighlighter;
    if (!contextCellHighlighter) {
      throw new Error('ContextCellHighlighter not initialized in AppState');
    }
    return contextCellHighlighter;
  },

  getChatContainer: (): NotebookChatContainer => {
    const chatContainer = AppStateService.getState().chatContainer;
    if (!chatContainer) {
      throw new Error('ChatContainer not initialized in AppState');
    }
    return chatContainer;
  },

  /**
   * Set the chat container
   */
  setChatContainer: (chatContainer: NotebookChatContainer) => {
    AppStateService.setState({ chatContainer });
  },

  /**
   * Get the chat container safely (returns null if not initialized)
   */
  getChatContainerSafe: (): NotebookChatContainer | null => {
    return AppStateService.getState().chatContainer;
  },

  /**
   * Set the chat service
   */
  setChatService: (chatService: IChatService) => {
    AppStateService.setState({ chatService });
  },

  getChatService: (): IChatService => {
    const chatService = AppStateService.getState().chatService;
    if (!chatService) {
      throw new Error('ChatService not initialized in AppState');
    }
    return chatService;
  },

  setConfig: (config: IConfig) => {
    AppStateService.setState({ config });
  },

  getConfig: (): IConfig => {
    const config = AppStateService.getState().config;
    if (!config) {
      throw new Error('Config not initialized in AppState');
    }
    return config;
  },

  /**
   * Update chat container with new notebook ID
   */
  updateChatContainerNotebookId: (
    oldNotebookId: string,
    newNotebookId: string
  ) => {
    const chatContainer = AppStateService.getState().chatContainer;
    if (chatContainer && !chatContainer.isDisposed) {
      chatContainer.updateNotebookId(oldNotebookId, newNotebookId);
    }
  },

  /**
   * Switch chat container to a notebook
   */
  switchChatContainerToNotebook: (notebookId: string) => {
    const chatContainer = AppStateService.getState().chatContainer;
    if (chatContainer && !chatContainer.isDisposed) {
      chatContainer.switchToNotebook(notebookId);
    }
  },

  /**
   * Find a notebook by its unique sage_ai.unique_id
   * @param uniqueId The unique ID to search for
   * @returns The notebook widget if found, null otherwise
   */
  getNotebookByID: async (uniqueId: string): Promise<NotebookPanel | null> => {
    const notebookTracker = AppStateService.getState().notebookTracker;
    const contentManager = AppStateService.getState().contentManager;

    if (!notebookTracker || !contentManager) {
      console.warn('NotebookTracker or ContentManager not initialized');
      return null;
    }

    // Convert forEach to a proper async iteration
    const notebooks: any[] = [];
    notebookTracker.forEach(notebook => {
      notebooks.push(notebook);
    });

    for (const notebook of notebooks) {
      try {
        const nbFile = await contentManager.get(notebook.context.path);
        if (nbFile) {
          const nbMetadata = nbFile.content.metadata || {};
          if (nbMetadata.sage_ai && nbMetadata.sage_ai.unique_id === uniqueId) {
            return notebook;
          }
        }
      } catch (error) {
        console.warn(
          `Error checking notebook ${notebook.context.path}:`,
          error
        );
      }
    }

    return notebookTracker.currentWidget;
  }
};

// Example usage:

// Read from state
// const { toolService, settings } = AppStateService.getState();

// Update state
// AppStateService.setState({ currentNotebookPath: '/path/to/notebook.ipynb' });

// Subscribe to changes
// AppStateService.changes.subscribe(state => {
//   console.log('New state!', state);
// });

// Use convenience methods
// const toolService = AppStateService.getToolService();
// AppStateService.updateSettings({ theme: 'dark' });
