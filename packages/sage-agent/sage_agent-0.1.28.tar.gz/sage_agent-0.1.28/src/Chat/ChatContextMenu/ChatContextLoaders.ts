/**
 * Constants and loading methods for chat context menu
 */
import { Contents, KernelMessage } from '@jupyterlab/services';
import { ToolService } from '../../Services/ToolService';
import { DatabaseMetadataCache } from '../../Services/DatabaseMetadataCache';
import { KernelPreviewUtils } from '../../utils/kernelPreview';

export interface MentionContext {
  type: 'rules' | 'data' | 'variable' | 'cell';
  id: string;
  name: string;
  content?: string;
  description?: string;
}

// Constants
export const VARIABLE_TYPE_BLACKLIST = [
  'module',
  'type',
  'function',
  'ZMQExitAutocall',
  'method'
];

export const VARIABLE_NAME_BLACKLIST = ['In', 'Out'];

export const MENTION_CATEGORIES = [
  {
    id: 'rules',
    name: 'Rules',
    icon: '📄',
    description: 'Reusable prompt templates'
  },
  {
    id: 'data',
    name: 'Data',
    icon: '📊',
    description: 'Dataset references and info'
  },
  {
    id: 'variables',
    name: 'Variables',
    icon: '🔤',
    description: 'Code variables and values'
  },
  {
    id: 'cells',
    name: 'Cells',
    icon: '📝',
    description: 'Notebook cell references'
  }
];

/**
 * Class responsible for loading different types of context items
 */
export class ChatContextLoaders {
  private contentManager: Contents.IManager;
  private toolService: ToolService;

  constructor(contentManager: Contents.IManager, toolService: ToolService) {
    this.contentManager = contentManager;
    this.toolService = toolService;
  }

  /**
   * Initialize context items for each category
   */
  public async initializeContextItems(): Promise<
    Map<string, MentionContext[]>
  > {
    const contextItems = new Map<string, MentionContext[]>();

    // Initialize empty maps for each category
    contextItems.set('rules', []);
    contextItems.set('data', [
      {
        type: 'data',
        id: 'demo-dataset',
        name: 'demo-dataset',
        description: 'Sample dataset for demonstration',
        content: 'This is a demo dataset context'
      }
    ]);
    contextItems.set('variables', [
      {
        type: 'variable',
        id: 'demo-var',
        name: 'demo_variable',
        description: 'Sample variable for demonstration',
        content: 'x = 42  # Demo variable'
      }
    ]);
    contextItems.set('cells', [
      {
        type: 'cell',
        id: 'demo-cell',
        name: 'Cell 1',
        description: 'Sample cell for demonstration',
        content: 'print("Hello from demo cell")'
      }
    ]);

    console.log(
      'All context items after initialization:',
      Array.from(contextItems.entries())
    ); // Debug log

    return contextItems;
  }

  /**
   * Load datasets from the data directory and include database metadata
   */
  public async loadDatasets(): Promise<MentionContext[]> {
    const datasetContexts: MentionContext[] = [];

    // First, try to add database metadata from cache (never retry pulling it)
    try {
      const dbCache = DatabaseMetadataCache.getInstance();
      const cachedMetadata = await dbCache.getCachedMetadata();
      const db_prompt =
        'This database schema is available for you to reference. When the user mentions custom data or asks about database-related tasks, use this schema as context. You can query this database in a code cell using sqlalchemy when appropriate.';
      if (cachedMetadata) {
        datasetContexts.push({
          type: 'data' as const,
          id: 'database-schema',
          name: 'Database Schema',
          description: 'Current database schema information',
          content: `${db_prompt} \n \n ${cachedMetadata}`
        });
        console.log(
          '[ChatContextLoaders] Added database schema to data contexts'
        );
      }
    } catch (error) {
      console.warn(
        '[ChatContextLoaders] Could not load database metadata:',
        error
      );
    }

    // Then load file-based datasets
    try {
      const datasets = await this.contentManager.get('./data');
      console.log('Loaded datasets:', datasets); // Debug log

      if (datasets.content && Array.isArray(datasets.content)) {
        const fileDatasets: MentionContext[] = await Promise.all(
          datasets.content
            .filter(file => file.type === 'file')
            .map(async file => {
              // remove everything from the last dot to the end (e.g. ".json", ".csv", ".txt", etc.)
              const name = file.name.replace(/\.[^/.]+$/, '');

              const content = await this.contentManager.get(
                './data/' + file.name
              );

              const contentString = `${content.content}`;

              return {
                type: 'data' as const,
                id: file.path,
                name,
                description: 'Dataset file',
                content: contentString.slice(0, 1000)
              };
            })
        );

        datasetContexts.push(...fileDatasets);
      }
    } catch (error) {
      console.error('Error loading datasets:', error);
    }

    return datasetContexts;
  }

  /**
   * Load notebook cells
   */
  public async loadCells(): Promise<MentionContext[]> {
    console.log('Loading cells... ======================');
    const notebook = this.toolService.getCurrentNotebook();
    if (!notebook) {
      console.warn('No notebook available');
      return [];
    }

    const cellContexts: MentionContext[] = [];
    const cells = notebook.widget.model.cells as any;

    for (const cell of cells) {
      console.log('Cell:', cell); // Debug log
      console.log('Cell metadata:', cell.metadata); // Debug log

      const tracker = cell.metadata.cell_tracker;
      if (tracker) {
        cellContexts.push({
          type: 'cell',
          id: tracker.trackingId,
          name: tracker.trackingId,
          description: '',
          content: cell.sharedModel.getSource()
        });
      }
    }

    console.log('CELL LOADING, cells:', cells); // Debug log
    return cellContexts;
  }

  /**
   * Load variables from the current kernel
   */
  public async loadVariables(): Promise<MentionContext[]> {
    console.log('Loading variables... ======================');
    const kernel = this.toolService.getCurrentNotebook()?.kernel;
    if (!kernel) {
      console.warn('No kernel available');
      return [];
    }

    try {
      // Use the shared kernel preview utilities to get detailed variable information
      const kernelVariables = await KernelPreviewUtils.getKernelVariables();
      
      if (!kernelVariables) {
        console.log('No kernel variables available');
        return [];
      }

      const variableContexts: MentionContext[] = [];
      
      for (const [varName, varInfo] of Object.entries(kernelVariables)) {
        // Skip variables in blacklists
        if (VARIABLE_NAME_BLACKLIST.includes(varName)) continue;
        if (VARIABLE_TYPE_BLACKLIST.includes(varInfo.type)) continue;

        // Create a description based on the variable info
        let description = varInfo.type || 'unknown';
        if (varInfo.shape) {
          description += ` (shape: ${JSON.stringify(varInfo.shape)})`;
        } else if (varInfo.size !== undefined && varInfo.size !== null) {
          description += ` (size: ${varInfo.size})`;
        }

        // Create content for the variable
        let content = '';
        if (varInfo.value !== undefined) {
          content = JSON.stringify(varInfo.value);
        } else if (varInfo.preview !== undefined) {
          content = JSON.stringify(varInfo.preview);
        } else if (varInfo.repr) {
          content = varInfo.repr;
        }

        variableContexts.push({
          type: 'variable',
          id: varName,
          name: varName,
          description: description,
          content: content
        });
      }

      console.log(`[ChatContextLoaders] Loaded ${variableContexts.length} variables`);
      return variableContexts;
    } catch (error) {
      console.error('Error loading variables:', error);
      return [];
    }
  }

  /**
   * Load template files from the templates directory
   */
  public async loadTemplateFiles(): Promise<MentionContext[]> {
    try {
      const files = await this.contentManager.get('./templates');

      if (files.content && Array.isArray(files.content)) {
        const templateContexts: MentionContext[] = files.content
          .filter(
            file => file.type === 'file' && file.name !== 'rule.example.md'
          )
          .map(file => {
            const displayName = file.name
              .replace(/^rule\./, '')
              .replace(/\.md$/, '');

            return {
              type: 'rules' as const,
              id: file.path,
              name: displayName,
              description: 'Rule file'
            };
          });

        return templateContexts;
      }
    } catch (error) {
      console.error('Error loading template files:', error);
    }

    return [];
  }

  /**
   * Load the content of a template file
   */
  public async loadTemplateContent(filePath: string): Promise<string> {
    try {
      const file = await this.contentManager.get(filePath, { content: true });
      if (file.content) {
        return typeof file.content === 'string'
          ? file.content
          : JSON.stringify(file.content);
      }
      return '';
    } catch (error) {
      console.error(`Error loading template file ${filePath}:`, error);
      return '';
    }
  }
}
