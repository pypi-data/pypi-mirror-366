import { Cell } from '@jupyterlab/cells';
import { CodeMirrorEditor } from '@jupyterlab/codemirror';
import { EditorView, ViewPlugin } from '@codemirror/view';
import { MergeView, unifiedMergeView } from '@codemirror/merge';
import {
  Extension,
  StateEffect,
  StateField,
  Transaction,
  Compartment
} from '@codemirror/state';

/**
 * Callback interface for merge operations
 */
export interface MergeCallbacks {
  /**
   * Called when a chunk is accepted
   * @param cellId The cell ID
   * @param newContent The new content
   */
  onAccept?: (cellId: string, newContent: string) => void;
  /**
   * Called when a chunk is rejected
   * @param cellId The cell ID
   * @param originalContent The original content
   */
  onReject?: (cellId: string, originalContent: string) => void;
  /**
   * Called when all chunks have been resolved, either accepted or rejected
   * @param cellId The cell ID
   * @param finalContent The final content
   */
  onAllResolved?: (cellId: string, finalContent: string) => void;
  /**
   * Called when all chunks have been rejected
   * @param cellId The cell ID
   * @param originalContent The original content
   */
  onRejectAll?: (cellId: string, originalContent: string) => void;
  /**
   * Called when all chunks have been resolved
   * @param cellId The cell ID
   * @param finalContent The final content
   */
  onApproveAll?: (cellId: string, finalContent: string) => void;
}

/**
 * Interface for merge view state information
 */
export interface MergeViewState {
  cellId: string;
  cell: Cell;
  view: CodeMirrorEditor;
  originalContent: string;
  initialChunkCount: number;
  acceptedChunkCount: number;
  rejectedChunkCount: number;
}

/**
 * PARTIAL MIGRATION: NotebookDiffTools.generateHtmlDiff → InlineDiffService
 *
 * This service provides a modern, CodeMirror-based inline diff experience
 * that replaces the previous HTML overlay approach using diff2html.
 *
 * Currently integrated in:
 * - ContextCellHighlighter.showDiffView() (✅ migrated for inline editing workflow)
 *
 * Original NotebookDiffTools workflow preserved for:
 * - NotebookDiffTools.display_diff() (uses original HTML overlays)
 * - DiffApprovalDialog (uses original generateHtmlDiff implementation)
 * - Diff manager workflows (continues to use existing approach)
 *
 * Migration Benefits (for migrated components):
 * - Better UX with CodeMirror's unified merge view (similar to Cursor)
 * - Native editor integration instead of HTML overlays
 * - Built-in accept/reject functionality via CodeMirror's merge controls
 * - Automatic theme support through CodeMirror
 * - Better performance and user interaction
 *
 * Future migration opportunities:
 * - Complete NotebookDiffTools.display_diff() migration
 * - Integrate with diff approval workflows
 * - Enhanced merge conflict resolution
 */

/**
 * Service for managing inline diffs in notebook cells using CodeMirror's unified merge view
 * This provides a Cursor-like inline diff experience with proper diff highlighting
 */
export class InlineDiffService {
  private activeMergeViews: Map<string, MergeViewState> = new Map();
  private mergeCallbacks: Map<string, MergeCallbacks> = new Map();
  private mergeCompartments: Map<string, Compartment> = new Map();

  /**
   * Count the number of merge chunks in the DOM
   * @param viewNode The editor view DOM node
   * @returns Number of merge chunks
   */
  private countMergeChunks(viewNode: HTMLElement): number {
    const chunkButtons = viewNode.querySelectorAll('.cm-chunkButtons');

    return chunkButtons.length;
  }

  /**
   * Get the initial chunk count for a cell after merge view is created
   * @param cell The notebook cell
   * @returns Number of initial merge chunks
   */
  private getInitialChunkCount(cell: Cell): number {
    if (cell.editor instanceof CodeMirrorEditor) {
      const viewNode = cell.editor.editor.contentDOM;
      if (viewNode) {
        return this.countMergeChunks(viewNode);
      }
    }
    return 0;
  }

  /**
   * Show inline diff for a cell using CodeMirror's unified merge view
   * @param cell The notebook cell
   * @param originalContent The original content to compare against
   * @param newContent The new/proposed content
   * @param callbacks Optional callbacks for merge operations
   *
   * Note: CodeMirror's merge view provides built-in accept/reject controls,
   * so no custom controls are added. Callbacks are used for programmatic interactions.
   */
  public showInlineDiff(
    cell: Cell,
    originalContent: string,
    newContent: string,
    callbacks?: MergeCallbacks
  ): void {
    const cellId = (cell.model.sharedModel.getMetadata()?.cell_tracker as any)
      .trackingId;
    console.log(
      `[InlineDiffService] Showing unified merge view for cell ${cellId}`
    );

    // Store callbacks
    if (callbacks) {
      this.mergeCallbacks.set(cellId, callbacks);
    }

    // Get the CodeMirror editor instance
    const editor = cell.editor;
    if (!editor || !(editor instanceof CodeMirrorEditor)) {
      console.error('Cell editor is not a CodeMirrorEditor instance');
      return;
    }

    // Store diff state with callbacks (initial chunk count will be set after DOM is ready)
    this.activeMergeViews.set(cellId, {
      cellId,
      cell,
      view: editor,
      originalContent: originalContent,
      initialChunkCount: 0,
      acceptedChunkCount: 0,
      rejectedChunkCount: 0
    });

    // Create the unified merge view
    this.createUnifiedMergeView(cell, originalContent, newContent);
  }

  /**
   * Create and configure the unified merge view
   */
  private createUnifiedMergeView(
    cell: Cell,
    originalContent: string,
    newContent: string
  ): void {
    const cellNode = cell.node;
    const editor = cell.editor as CodeMirrorEditor;
    const cellId = (cell.model.sharedModel.getMetadata()?.cell_tracker as any)
      .trackingId;

    // Add a class to indicate diff mode
    cellNode.classList.add('sage-ai-unified-diff-active');

    try {
      // Get the current editor view
      const currentView = editor.editor;

      // Set the new content first
      cell.model.sharedModel.setSource(newContent);

      // Create a state field to track merge operations
      const mergeTracker = StateField.define({
        create: () => ({
          lastContent: newContent,
          hasTrackedCompletion: false
        }),
        update: (value, transaction) => {
          // Listen for merge library dispatch events
          const userEvent = transaction.annotation(Transaction.userEvent);
          const mergeViewState = this.activeMergeViews.get(cellId);
          const callbacks = this.mergeCallbacks.get(cellId);

          if (mergeViewState && callbacks && userEvent) {
            if (userEvent === 'accept') {
              // Chunk was accepted
              mergeViewState.acceptedChunkCount++;
              console.log(
                `[InlineDiffService] Chunk accepted in cell ${cellId}. Total accepted: ${mergeViewState.acceptedChunkCount}`
              );

              // Fire individual onAccept callback
              const currentContent = transaction.newDoc.toString();
              setTimeout(() => callbacks.onAccept?.(cellId, currentContent), 0);
            } else if (userEvent === 'revert') {
              // Chunk was rejected
              mergeViewState.rejectedChunkCount++;
              console.log(
                `[InlineDiffService] Chunk rejected in cell ${cellId}. Total rejected: ${mergeViewState.rejectedChunkCount}`
              );

              // Fire individual onReject callback
              setTimeout(
                () =>
                  callbacks.onReject?.(cellId, mergeViewState.originalContent),
                0
              );
            }

            // Check if all chunks have been resolved
            const totalResolved =
              mergeViewState.acceptedChunkCount +
              mergeViewState.rejectedChunkCount;
            if (
              totalResolved >= mergeViewState.initialChunkCount &&
              mergeViewState.initialChunkCount > 0 &&
              !value.hasTrackedCompletion
            ) {
              const currentContent = transaction.newDoc.toString();

              // Determine the type of completion
              if (
                mergeViewState.rejectedChunkCount ===
                mergeViewState.initialChunkCount
              ) {
                // All chunks were rejected
                setTimeout(() => {
                  if (callbacks.onRejectAll) {
                    callbacks.onRejectAll(
                      cellId,
                      mergeViewState.originalContent
                    );
                  }
                }, 0);
              } else if (
                mergeViewState.acceptedChunkCount ===
                mergeViewState.initialChunkCount
              ) {
                // All chunks were accepted
                setTimeout(() => {
                  if (callbacks.onApproveAll) {
                    callbacks.onApproveAll(cellId, currentContent);
                  }
                }, 0);
              } else {
                // Mixed resolution (some accepted, some rejected)
                setTimeout(() => {
                  if (callbacks.onAllResolved) {
                    callbacks.onAllResolved(cellId, currentContent);
                  }
                }, 0);
              }

              // Mark that we've tracked the completion
              value = { ...value, hasTrackedCompletion: true };
            }
          }

          // Check if merge view should be cleaned up after changes
          if (transaction.docChanged) {
            setTimeout(() => {
              this.cleanupMergeViewIfEmpty(cell);
            }, 150); // Allow time for DOM updates
          }

          return {
            lastContent: transaction.newDoc.toString(),
            hasTrackedCompletion: value.hasTrackedCompletion
          };
        }
      });

      // Create unified merge view extension
      const mergeExtension = unifiedMergeView({
        original: originalContent,
        gutter: false,
        mergeControls: true,
        highlightChanges: true,
        syntaxHighlightDeletions: true,
        allowInlineDiffs: true
      });

      // Create the monitoring plugin for this specific cell
      const monitorPlugin = this.createMergeViewMonitor(cell);

      // Apply the merge view extension with change tracking and monitoring
      this.extendEditorExtensions(
        currentView,
        [mergeExtension, mergeTracker, monitorPlugin],
        cellId
      );

      if (originalContent) {
        cell.node.classList.remove('code-mirror-empty-original-content');
      } else {
        cell.node.classList.add('code-mirror-empty-original-content');
      }

      // Update initial chunk count after DOM is ready
      setTimeout(() => {
        const mergeViewState = this.activeMergeViews.get(cellId);
        if (mergeViewState) {
          const initialChunkCount = this.getInitialChunkCount(cell);
          mergeViewState.initialChunkCount = initialChunkCount;
          console.log(
            `[InlineDiffService] Initial chunk count for cell ${cellId}: ${initialChunkCount}`
          );
        }
      }, 100); // Allow time for DOM to be populated with merge chunks
    } catch (error) {
      console.error('Error creating unified merge view:', error);
    }
  }

  /**
   * Reconfigure the editor to include the merge view extension using a compartment
   */
  private extendEditorExtensions(
    currentView: EditorView,
    extensions: Extension[],
    cellId: string
  ): void {
    // Create a compartment for this merge view so it can be easily removed
    const compartment = new Compartment();
    this.mergeCompartments.set(cellId, compartment);

    // Use the compartment to add the merge view extensions
    currentView.dispatch({
      effects: StateEffect.appendConfig.of(compartment.of(extensions))
    });

    console.log(
      '[InlineDiffService] Configured unified merge view with change tracking'
    );
  }

  /**
   * Check if there are any remaining merge chunks in the DOM
   */
  private hasRemainingMergeChunks(viewNode: HTMLElement): boolean {
    // Check for merge chunks in the DOM
    const deletedChunks = viewNode.querySelectorAll('.cm-deletedChunk');
    const changedLines = viewNode.querySelectorAll('.cm-changedLine');

    return deletedChunks.length > 0 || changedLines.length > 0;
  }

  /**
   * Remove merge extensions from a cell's editor view
   */
  public removeMergeExtensions(cell: Cell): void {
    const cellId = (cell.model.sharedModel.getMetadata()?.cell_tracker as any)
      .trackingId;
    const compartment = this.mergeCompartments.get(cellId);

    if (compartment && cell.editor instanceof CodeMirrorEditor) {
      const currentView = cell.editor.editor;

      // Remove the merge extensions by reconfiguring the compartment to empty
      currentView.dispatch({
        effects: compartment.reconfigure([])
      });

      // Clean up stored references
      this.mergeCompartments.delete(cellId);
      this.mergeCallbacks.delete(cellId);
      this.activeMergeViews.delete(cellId);

      // Remove the diff mode class
      cell.node.classList.remove('sage-ai-unified-diff-active');

      console.log(
        `[InlineDiffService] Removed merge extensions for cell ${cellId}`
      );
    }
  }

  /**
   * Clean up merge view for a cell if no chunks remain
   */
  public cleanupMergeViewIfEmpty(cell: Cell): boolean {
    const cellId = (cell.model.sharedModel.getMetadata()?.cell_tracker as any)
      .trackingId;
    const mergeView = this.activeMergeViews.get(cellId);

    if (
      mergeView &&
      !this.hasRemainingMergeChunks(mergeView.view.editor.contentDOM!)
    ) {
      // Get the final content before cleanup
      const finalContent = cell.model.sharedModel.getSource();

      // Get callbacks before cleanup
      const callbacks = this.mergeCallbacks.get(cellId);

      // No chunks remain, remove the merge extensions completely
      this.removeMergeExtensions(cell);

      // Call onAllResolved callback if provided
      if (callbacks?.onAllResolved) {
        callbacks.onAllResolved(cellId, finalContent);
      }

      return true;
    }

    return false;
  }

  /**
   * Monitor merge view and auto-cleanup when chunks are resolved
   */
  private createMergeViewMonitor(cell: Cell): ViewPlugin<any> {
    return ViewPlugin.define(() => ({
      update: () => {
        // Check if all chunks have been resolved after each update
        setTimeout(() => {
          this.cleanupMergeViewIfEmpty(cell);
        }, 100); // Small delay to let DOM updates complete
      }
    }));
  }
}

// Global singleton instance
export const inlineDiffService = new InlineDiffService();
