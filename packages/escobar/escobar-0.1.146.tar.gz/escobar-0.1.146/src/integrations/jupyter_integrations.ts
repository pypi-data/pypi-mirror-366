import { JupyterFrontEnd } from '@jupyterlab/application';
import { Contents } from '@jupyterlab/services';
import { NotebookPanel, NotebookModel, NotebookActions } from '@jupyterlab/notebook';
import { Cell, CellModel, ICellModel, CodeCell, MarkdownCell } from '@jupyterlab/cells';
import { ICodeCellModel, IMarkdownCellModel } from '@jupyterlab/cells';
import { callPython, registerFunction, get_ws } from '../voitta/pythonBridge_browser'
import { Widget } from '@lumino/widgets';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { FileEditor } from '@jupyterlab/fileeditor';
import { MainAreaWidget } from '@jupyterlab/apputils';
import { IDocumentWidget } from '@jupyterlab/docregistry';

import { init_fs, ensurePathExists } from "./jupyter_integrations_fs"
import { init_terminal, findTerminalByName } from "./jupyter_integrations_terminal"
import { init_cells } from "./jupyter_integrations_cells"
import { init_output } from "./jupyter_integrations_output"
import { init_settings } from "./jupyter_integrations_settings"
import { init_diff } from "./jupyter_integrations_diff"
import { init_debugger } from "./jupyter_integrations_debugger"

import { INotebookTracker } from '@jupyterlab/notebook'
import { IDebugger } from '@jupyterlab/debugger';

export var streamingState = {}

export var app: JupyterFrontEnd | undefined;
export var notebookTracker: INotebookTracker | undefined;
export var debuggerService: IDebugger | undefined;
export var memoryBank = {};

export const functions = {}
init_fs()
init_terminal()
init_cells()
init_output()
init_settings()
init_diff()
init_debugger()

const O: { [key: string]: (...args: any[]) => any } = {};

var functions_registred = false;

/**
 * Get the currently active notebook panel using the app
 */
export function getActiveNotebook(jupyterApp: JupyterFrontEnd): NotebookPanel | null {
  const { shell } = jupyterApp;
  const widget = shell.currentWidget;

  if (!widget) {
    return null;
  }

  // Check if the current widget is a notebook panel
  if (widget instanceof NotebookPanel) {
    return widget;
  }

  return null;
}

/**
 * Get the currently active notebook panel using the notebookTracker
 */
export function getActiveNotebookFromTracker(): NotebookPanel | null {
  if (!notebookTracker) {
    return null;
  }

  return notebookTracker.currentWidget;
}

/**
 * Validate a cell index in a notebook
 */
export function validateCellIndex(notebook: NotebookPanel, index: number): boolean {
  if (!notebook || !notebook.content) {
    return false;
  }

  const count = notebook.content.widgets.length;
  return index >= 0 && index < count;
}

export async function register_functions(
  _app: JupyterFrontEnd,
  _notebookTracker: INotebookTracker,
  _debuggerService: IDebugger
) {
  console.log("=============== register_functions ===============");
  app = _app;
  notebookTracker = _notebookTracker;
  debuggerService = _debuggerService;


  for (const name of Object.keys(functions)) {
    console.log("register function:", name);
    registerFunction(name, true, functions[name]["func"], functions[name], true);
  }
}

export async function get_tools(app: JupyterFrontEnd,
  notebookTracker: INotebookTracker, debuggerService: IDebugger) {
  if (!(functions_registred)) {
    await register_functions(app, notebookTracker, debuggerService);
    functions_registred = true;
  }
  const tools = [];
  for (const func of Object.values(functions)) {
    tools.push(func["def"]);
  }
  return tools;
}


export async function get_opened_tabs(): Promise<any[]> {
  const mainAreaWidgets = app.shell.widgets('main');

  const currentWidget = app.shell.currentWidget;

  const openedTabs = [];
  //const widgets = []


  Array.from(mainAreaWidgets).forEach(widget => {
    let tabInfo = {
      id: widget.id,
      title: widget.title.label || 'Untitled',
      type: 'unknown',
      isVisible: false
    };



    // Determine widget type
    if (widget instanceof NotebookPanel) {
      tabInfo.type = 'notebook';
      tabInfo['path'] = (widget.context?.path) || '';
    } else if (widget instanceof FileEditor ||
      (widget as any).context?.path?.includes('.')) {
      tabInfo.type = 'file';
      tabInfo['path'] = (widget as any).context?.path || '';
    } else if (widget.id.startsWith('terminal') ||
      widget.title?.label?.toLowerCase().includes('terminal')) {
      tabInfo.type = 'terminal';
      tabInfo['name'] = widget.title.label.replace('Terminal ', '') || '';
    }

    tabInfo["isVisible"] = widget.isVisible;
    openedTabs.push(tabInfo);

  });

  return openedTabs;
}



functions["listAvailableKernels"] = {
  "def": {
    "name": "listAvailableKernels",
    "description": "Lists kernels (such as python) available on the system",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    const kernelSpecs = await app.serviceManager.kernelspecs.refreshSpecs();
    await app.serviceManager.kernelspecs.refreshSpecs();
    const specs = app.serviceManager.kernelspecs.specs?.kernelspecs;

    const result = Object.values(specs).map(spec => ({
      name: spec.name,
      display_name: spec.display_name,
      language: spec.language
    }));

    return JSON.stringify(result);
  }
}


functions["createAndOpenNotebook"] = {
  "def": {
    "name": "createAndOpenNotebook",
    "description": "Creates and opens a new notebook",
    "arguments": {
      "name": {
        "type": "string",
        "name": "Name for the new notebook"
      },
      "kernelName": {
        "type": "string",
        "name": "Name of kernel to use"
      }
    }
  },
  "func": async (args: any): Promise<string> => {
    let name = args["name"];
    const kernelName = args["kernelName"];
    const contents = app.serviceManager.contents;
    const kernelspecs = app.serviceManager.kernelspecs.specs?.kernelspecs;

    if (!name.endsWith('.ipynb')) {
      name += '.ipynb';
    }

    const path = name.startsWith('./') ? name.slice(2) : name;

    // Get display_name and language from kernel specs (fallback to name)
    const kernelSpec = kernelspecs?.[kernelName];
    const displayName = kernelSpec?.display_name ?? kernelName;
    const language = kernelSpec?.language ?? "python";

    try {
      await contents.get(path);
    } catch (err: any) {
      if (err.response?.status === 404) {
        // Notebook doesn't exist — create with metadata
        await contents.save(path, {
          type: 'notebook',
          format: 'json',
          content: {
            cells: [],
            metadata: {
              kernelspec: {
                name: kernelName,
                display_name: displayName,
                language: language
              }
            },
            nbformat: 4,
            nbformat_minor: 5
          }
        });
      } else {
        console.error(err);
        return "There was an error retrieving notebook info.";
      }
    }

    // Open the notebook and attach the kernel
    await app.commands.execute('docmanager:open', {
      path,
      factory: 'Notebook',
      options: {
        kernel: {
          name: kernelName
        }
      }
    });

    return "done";
  }
};



functions["openNotebook"] = {
  "def": {
    "name": "openNotebook",
    "description": "Opens an existing notebook",
    "arguments": {
      "name": {
        "type": "string",
        "name": "Name for the notebook to open"
      }
    }
  },
  "func": async (args: any): Promise<string> => {
    const name = args.name;
    const contents = app.serviceManager.contents;

    try {
      await contents.get(name);
    } catch (err) {
      return `Notebook ${name} does not exit`
    }

    await app.commands.execute('docmanager:open', {
      path: name,
      factory: 'Notebook'
    });
    return "done";
  }
}


functions["restartKernel"] = {
  "def": {
    "name": "restartKernel",
    "description": "Restart the kernel of the active notebook",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    if (!app) {
      return JSON.stringify({ error: "JupyterLab app not initialized" });
    }

    const notebook = getActiveNotebook(app);

    if (!notebook || !notebook.sessionContext) {
      return JSON.stringify({ error: "No active notebook found" });
    }

    try {
      // Restart the kernel
      if (notebook.sessionContext.session?.kernel) {
        await notebook.sessionContext.session.kernel.restart();
      } else {
        throw new Error("No kernel available to restart");
      }

      return JSON.stringify({
        success: true,
        message: "Kernel restarted successfully"
      });
    } catch (error) {
      return JSON.stringify({
        error: `Error restarting kernel: ${error.message}`
      });
    }
  }
}

functions["stopExecution"] = {
  "def": {
    "name": "stopExecution",
    "description": "Stop the execution of the active notebook by interrupting the kernel",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    if (!app) {
      return JSON.stringify({ error: "JupyterLab app not initialized" });
    }

    const notebook = getActiveNotebook(app);

    if (!notebook || !notebook.sessionContext) {
      return JSON.stringify({ error: "No active notebook found" });
    }

    try {
      // Interrupt the kernel
      await notebook.sessionContext.session?.kernel?.interrupt();

      return JSON.stringify({
        success: true,
        message: "Execution interrupted"
      });
    } catch (error) {
      return JSON.stringify({
        error: `Error interrupting kernel: ${error.message}`
      });
    }
  }
}

functions["getCurrentNotebook"] = {
  "def": {
    "name": "getCurrentNotebook",
    "description": "Gets information about the currently open notebook",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    if (!app) {
      return JSON.stringify({ error: "JupyterLab app not initialized" });
    }

    const notebook = getActiveNotebook(app);

    if (!notebook || !notebook.content) {
      return JSON.stringify({ error: "No active notebook found" });
    }

    try {
      // Get notebook information
      const context = notebook.context;
      const model = notebook.model;
      const path = context.path;
      const name = path.split('/').pop() || '';
      const dirty = context.model.dirty;

      // Get basic metadata if available
      let metadata = {};
      if (model && (model as NotebookModel).metadata) {
        // Just include a simplified version of metadata
        try {
          const nbModel = model as NotebookModel;
          // Create a simple object with basic metadata properties
          metadata = {
            kernelName: nbModel.metadata.kernelName || '',
            kernelLanguage: nbModel.metadata.kernelLanguage || '',
            // Add other metadata properties as needed
          };
        } catch (err) {
          console.error('Error extracting notebook metadata:', err);
        }
      }

      return JSON.stringify({
        success: true,
        notebook: {
          path: path,
          name: name,
          dirty: dirty,
          metadata: metadata,
          cell_count: model.cells.length
        }
      });
    } catch (error) {
      return JSON.stringify({
        error: `Error getting notebook information: ${error.message}`
      });
    }
  }
}

functions["getKernelState"] = {
  "def": {
    "name": "getKernelState",
    "description": "Get the state of the kernel and information about any currently executing cell",
    "arguments": {}
  },
  "func": async (args: any): Promise<string> => {
    if (!app) {
      return JSON.stringify({ error: "JupyterLab app not initialized" });
    }

    const notebook = getActiveNotebook(app);

    if (!notebook || !notebook.sessionContext) {
      return JSON.stringify({ error: "No active notebook found" });
    }

    try {
      const session = notebook.sessionContext.session;
      const kernel = session?.kernel;

      if (!kernel) {
        return JSON.stringify({
          success: true,
          kernel_state: "no_kernel",
          executing: false
        });
      }

      // Get kernel status
      const status = kernel.status;

      // Check for executing cells
      const executingCells = [];
      const cells = notebook.content.widgets;

      for (let i = 0; i < cells.length; i++) {
        const cell = cells[i];
        if (cell instanceof CodeCell && cell.model.executionCount !== null && cell.hasClass('jp-mod-executing')) {
          executingCells.push({
            index: i,
            execution_count: cell.model.executionCount
          });
        }
      }

      return JSON.stringify({
        success: true,
        kernel_state: status,
        executing: status === 'busy',
        executing_cells: executingCells
      });
    } catch (error) {
      return JSON.stringify({
        error: `Error getting kernel state: ${error.message}`
      });
    }
  }
}

