import { JupyterFrontEnd } from '@jupyterlab/application';
import { app, functions } from './jupyter_integrations';
import { streamingState } from "./jupyter_integrations";
import { CodeMirrorEditor, jupyterTheme, jupyterHighlightStyle } from '@jupyterlab/codemirror';
import { Widget } from '@lumino/widgets';

// Import necessary CodeMirror modules
import { StateEffect, StateField, EditorState, Text, Extension, Compartment } from '@codemirror/state';
import { Decoration, EditorView, ViewPlugin } from '@codemirror/view';
import { MergeView } from '@codemirror/merge';
import { LanguageSupport, syntaxHighlighting } from '@codemirror/language';

// Import language support modules
import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import { json } from '@codemirror/lang-json';
import { markdown } from '@codemirror/lang-markdown';
import { html } from '@codemirror/lang-html';
import { css } from '@codemirror/lang-css';

// Import diff utilities from the llm-diff-utils module



function unescapeString(input: string): string {
    // Return early for null, undefined, or empty string
    if (input === null || input === undefined) {
        return '';
    }

    if (input === '') {
        return '';
    }

    return input.replace(/\\"/g, '"')
        .replace(/\\'/g, "'")
        .replace(/\\\\/g, '\\')
        .replace(/\\n/g, '\n')
        .replace(/\\t/g, '\t')
        .replace(/\\r/g, '\r')
        .replace(/\\b/g, '\b')
        .replace(/\\f/g, '\f')
        .replace(/\\v/g, '\v')
        .replace(/\\0/g, '\0')
        .replace(/\\x([0-9A-Fa-f]{2})/g, (_, hex) =>
            String.fromCharCode(parseInt(hex, 16))
        )
        .replace(/\\u([0-9A-Fa-f]{4})/g, (_, hex) =>
            String.fromCharCode(parseInt(hex, 16))
        )
        .replace(/\\u\{([0-9A-Fa-f]+)\}/g, (_, hex) =>
            String.fromCodePoint(parseInt(hex, 16))
        )
        .replace(/\\([0-3][0-7]{2}|[0-7]{1,2})/g, (_, octal) =>
            String.fromCharCode(parseInt(octal, 8))
        );
}

function shouldUnescapeReplacement(replaceText: string, filePath: string): boolean {
    // Return early for null, undefined, or empty string
    if (!replaceText || replaceText === '') {
        return false;
    }

    // Get file extension to determine file type
    const fileExtension = filePath.split('.').pop()?.toLowerCase() || '';

    // File types that typically need unescaping (JSON, config files, etc.)
    const unescapeFileTypes = ['json', 'jsonc', 'yaml', 'yml', 'toml', 'ini', 'cfg', 'conf'];

    // If it's a file type that typically contains escaped strings, check content
    if (unescapeFileTypes.includes(fileExtension)) {
        return true;
    }

    // For other file types, only unescape if the text looks like it contains intentional escape sequences
    // This is a heuristic: if the text contains multiple escape sequences that look intentional
    const escapePatterns = [
        /\\"/g,     // Escaped quotes
        /\\'/g,     // Escaped single quotes  
        /\\t/g,     // Escaped tabs
        /\\r/g,     // Escaped carriage returns
        /\\x[0-9A-Fa-f]{2}/g,  // Hex escapes
        /\\u[0-9A-Fa-f]{4}/g,  // Unicode escapes
        /\\u\{[0-9A-Fa-f]+\}/g // Unicode code point escapes
    ];

    // Count how many different types of escape sequences we find
    let escapeTypeCount = 0;
    for (const pattern of escapePatterns) {
        if (pattern.test(replaceText)) {
            escapeTypeCount++;
        }
    }

    // Only unescape if we find multiple types of escape sequences (indicating intentional escaping)
    // OR if the text starts and ends with quotes (indicating it's a string literal)
    const looksLikeEscapedString = escapeTypeCount >= 2 ||
        (replaceText.startsWith('"') && replaceText.endsWith('"')) ||
        (replaceText.startsWith("'") && replaceText.endsWith("'"));

    return looksLikeEscapedString;
}

// Simple function to extract text content from file
function extractTextContent(fileContent: any, filePath: string): string {
    // Handle different content formats
    if (typeof fileContent.content === 'string') {
        return fileContent.content;
    }

    // Handle base64 encoded files
    if (fileContent.format === 'base64' && typeof fileContent.content === 'string') {
        try {
            return atob(fileContent.content);
        } catch (err) {
            throw new Error(`Failed to decode base64 content for ${filePath}: ${err.message}`);
        }
    }

    // If content is object, stringify it (fallback for any remaining edge cases)
    if (typeof fileContent.content === 'object' && fileContent.content !== null) {
        try {
            return JSON.stringify(fileContent.content, null, 2);
        } catch (err) {
            throw new Error(`Failed to stringify content for ${filePath}: ${err.message}`);
        }
    }

    throw new Error(`Unsupported content format for ${filePath}: ${typeof fileContent.content}`);
}


function ensureString(value: any, context: string): string {
    if (value === null || value === undefined) {
        console.warn(`${context}: value is null/undefined, using empty string`);
        return '';
    }
    if (typeof value !== 'string') {
        console.warn(`${context}: value is not a string (${typeof value}), converting`);
        return String(value);
    }
    return value;
}


function createMergeViewSafely(originalContent: string, diffResult: string, languageExtensions: any[], filePath: string): MergeView {
    // Validate inputs with detailed logging
    const safeOriginal = ensureString(originalContent, `originalContent for ${filePath}`);
    const safeDiff = ensureString(diffResult, `diffResult for ${filePath}`);


    try {
        const mergeView = new MergeView({
            a: {
                doc: safeOriginal,
                extensions: languageExtensions
            },
            b: {
                doc: safeDiff,
                extensions: languageExtensions
            },
            highlightChanges: true
        });

        return mergeView;
    } catch (err) {
        const errorDetails = {
            filePath,
            originalType: typeof safeOriginal,
            diffType: typeof safeDiff,
            originalLength: safeOriginal?.length,
            diffLength: safeDiff?.length,
            originalSample: safeOriginal?.substring(0, 100),
            diffSample: safeDiff?.substring(0, 100),
            error: err.message,
            stack: err.stack
        };

        console.error("MergeView creation failed:", errorDetails);
        throw new Error(`MergeView creation failed for ${filePath}: ${err.message}`);
    }
}

function safeStringReplace(content: string, search: string, replace: string, context: string): { result: string, changePosition?: { line: number, ch: number } } {
    const safeContent = ensureString(content, `content for ${context}`);
    const safeSearch = ensureString(search, `search string for ${context}`);
    const safeReplace = ensureString(replace, `replace string for ${context}`);

    try {
        // Extract file path from context for conditional unescaping
        const filePath = context.split(' ')[0] || '';

        if (safeSearch === '+') {
            // Append: change is at the end of content
            const lines = safeContent.split('\n');
            const lastLineIndex = lines.length - 1;
            const lastLineLength = lines[lastLineIndex].length;

            // Conditionally unescape based on file type and content
            const finalReplace = shouldUnescapeReplacement(safeReplace, filePath)
                ? unescapeString(safeReplace)
                : safeReplace;
            const result = safeContent + finalReplace;

            return {
                result: result,
                changePosition: { line: lastLineIndex, ch: lastLineLength }
            };
        } else if (safeSearch === '-') {
            // Prepend: change is at the beginning
            const finalReplace = shouldUnescapeReplacement(safeReplace, filePath)
                ? unescapeString(safeReplace)
                : safeReplace;
            const result = finalReplace + safeContent;

            return {
                result: result,
                changePosition: { line: 0, ch: 0 }
            };
        } else {
            // Regular search/replace: find the position of the change
            const searchIndex = safeContent.indexOf(safeSearch);

            let changePosition: { line: number, ch: number } | undefined;

            if (searchIndex >= 0) {
                // Calculate line and column position
                const beforeChange = safeContent.substring(0, searchIndex);
                const lines = beforeChange.split('\n');
                changePosition = {
                    line: lines.length - 1,
                    ch: lines[lines.length - 1].length
                };
            } else {
                console.warn(`⚠️ STRING-REPLACE: Search string not found in content for ${context}`);
            }

            // Conditionally unescape based on file type and content
            const finalReplace = shouldUnescapeReplacement(safeReplace, filePath)
                ? unescapeString(safeReplace)
                : safeReplace;
            const result = safeContent.replace(safeSearch, finalReplace);

            return { result, changePosition };
        }
    } catch (err) {
        console.error(`❌ STRING-REPLACE: Replacement failed for ${context}:`, err.message);
        throw new Error(`String replacement failed for ${context}: ${err.message}`);
    }
}


// Debug function to log information about the editor state
function debugEditorState(editor: EditorView, label: string) {
    console.log(`Debug ${label}:`, {
        hasFocus: editor.hasFocus,
        docLength: editor.state.doc.length
    });
}

// Function to get language extensions for a file based on its extension
function getLanguageExtensionsForFile(filePath: string): Extension[] {
    const fileExtension = filePath.split('.').pop()?.toLowerCase() || '';
    const extensions: Extension[] = [];

    // Always add JupyterLab's syntax highlighting
    extensions.push(syntaxHighlighting(jupyterHighlightStyle));

    // Add language support based on file extension
    let languageSupport: Extension | null = null;

    switch (fileExtension) {
        case 'py':
            languageSupport = python();
            break;
        case 'js':
            languageSupport = javascript();
            break;
        case 'ts':
            languageSupport = javascript({ typescript: true });
            break;
        case 'jsx':
            languageSupport = javascript({ jsx: true });
            break;
        case 'tsx':
            languageSupport = javascript({ jsx: true, typescript: true });
            break;
        case 'json':
            languageSupport = json();
            break;
        case 'md':
            languageSupport = markdown();
            break;
        case 'html':
        case 'htm':
            languageSupport = html();
            break;
        case 'css':
            languageSupport = css();
            break;
        // Add more language support as needed
    }

    if (languageSupport) {
        extensions.push(languageSupport);
        console.log(`Added language support for ${fileExtension}`);
    } else {
        console.log(`No specific language support for ${fileExtension}, using default highlighting`);
    }

    return extensions;
}

var mergeViews = {};
var mergeWidgets = {}

// Streaming content state management
var streamingContent = new Map<string, string>();
var streamingCallIds = new Map<string, string>(); // Maps filePath to current call_id
var fileBaselines = new Map<string, string>(); // Maps filePath to original baseline content (never modified)

async function getTextContentFromModel(filePath: string): Promise<string> {
    // Reject actual notebook files
    if (filePath.endsWith('.ipynb')) {
        throw new Error(`Cannot edit .ipynb files directly. Use Jupytext to convert to text format first.`);
    }

    // Find document context for the file
    const context = findDocumentContext(filePath);

    // Wait for both context and model to be ready
    if (context.ready) {
        await context.ready;
    }
    if (context.model?.ready) {
        await context.model.ready;
    }

    const model = context.model;

    // Method 1: Use model's toString() if available (works for Jupytext text files)
    if (typeof model.toString === 'function') {
        return model.toString();
    }

    // Method 2: Use model's value.text for text files
    if (model.value?.text !== undefined) {
        return model.value.text;
    }

    // If neither work, this isn't a text file
    throw new Error(`File ${filePath} is not a text file or doesn't have accessible text content`);
}

function findDocumentContext(filePath: string): any {
    const widgets = app.shell.widgets('main');

    for (const widget of widgets) {
        const context = (widget as any).context;
        if (context && context.path === filePath) {
            return context;
        }
    }

    // Also check by widget title for edge cases
    for (const widget of widgets) {
        if (widget.title?.label?.includes(filePath.split('/').pop() || '')) {
            const context = (widget as any).context;
            if (context && context.path === filePath) {
                return context;
            }
        }
    }

    throw new Error(`No open document context found for ${filePath}. File must be open in JupyterLab.`);
}

async function saveTextContentToModel(context: any, content: string, filePath: string): Promise<boolean> {
    // Reject actual notebook files
    if (filePath.endsWith('.ipynb')) {
        throw new Error(`Cannot save .ipynb files directly. Use Jupytext format instead.`);
    }

    const model = context.model;

    // Method 1: Use fromString() if available (Jupytext and text files)
    if (typeof model.fromString === 'function') {
        model.fromString(content);
        await context.save();
        return true;
    }

    // Method 2: Set value.text for text models
    if (model.value?.text !== undefined) {
        model.value.text = content;
        await context.save();
        return true;
    }

    throw new Error(`Cannot save text content to ${filePath} - not a text file model`);
}

export function init_diff() {
    functions["diffToFile"] = {
        "def": {
            "name": "diffToFile",
            "description": "Makes tagreted change in file. Search must match the entire piece exactly. Use it in as a diff",
            "arguments": {
                "filePath": {
                    "type": "string",
                    "name": "Relative path to the file to display in merge view. Relative! "
                },
                "search": {
                    "type": "string",
                    "name": "text to be removed. text should be long enough to ensure unique match. Pass '+' string to append to file, '-' to add at the beginning"
                },
                "replace": {
                    "type": "string",
                    "name": "text to insert instead of the removed text"
                }
            }
        },
        "func": async (args: any, streaming: boolean = false, call_id: string = undefined): Promise<string> => {
            function scrollToChangeOnce(mergeView: MergeView, position: { line: number, ch: number }): void {
                try {
                    if (!mergeView || !position) {
                        return;
                    }

                    // Calculate the document position from line/column
                    const docA = mergeView.a.state.doc;
                    const docB = mergeView.b.state.doc;

                    // Ensure line number is within bounds
                    const lineA = Math.min(position.line, docA.lines - 1);
                    const lineB = Math.min(position.line, docB.lines - 1);

                    // Get the line start position
                    const posA = docA.line(lineA + 1).from + Math.min(position.ch, docA.line(lineA + 1).length);
                    const posB = docB.line(lineB + 1).from + Math.min(position.ch, docB.line(lineB + 1).length);

                    // Scroll both editors so the edit line appears as the second line from top
                    mergeView.a.dispatch({
                        effects: EditorView.scrollIntoView(posA, { y: 'start', yMargin: 30 })
                    });

                    mergeView.b.dispatch({
                        effects: EditorView.scrollIntoView(posB, { y: 'start', yMargin: 30 })
                    });

                    console.log(`📍 Scrolled to change at line ${position.line}, column ${position.ch} (positioned as second line from top)`);
                } catch (err) {
                    console.warn('Could not scroll to change position:', err.message);
                }
            }

            function smartFollowScroll(mergeView: MergeView, position: { line: number, ch: number }): void {
                try {
                    if (!mergeView || !position) {
                        return;
                    }

                    // Get viewport and document info for the modified editor (B)
                    const editorB = mergeView.b;
                    const doc = editorB.state.doc;
                    const viewport = editorB.viewport;

                    // Calculate which line we're editing
                    const editLine = position.line;

                    // Find the last fully visible line in the viewport
                    const lastVisiblePos = viewport.to;
                    const lastVisibleLine = doc.lineAt(lastVisiblePos).number - 1; // Convert to 0-based


                    // Check if edit line is below the visible viewport
                    if (editLine > lastVisibleLine) {
                        // Edit is below screen - scroll so edit line becomes the last visible line
                        const lineA = Math.min(position.line, mergeView.a.state.doc.lines - 1);
                        const lineB = Math.min(position.line, doc.lines - 1);

                        const posA = mergeView.a.state.doc.line(lineA + 1).from + Math.min(position.ch, mergeView.a.state.doc.line(lineA + 1).length);
                        const posB = doc.line(lineB + 1).from + Math.min(position.ch, doc.line(lineB + 1).length);

                        // Scroll so the edit line appears as the last visible line
                        mergeView.a.dispatch({
                            effects: EditorView.scrollIntoView(posA, { y: 'end', yMargin: 20 })
                        });

                        mergeView.b.dispatch({
                            effects: EditorView.scrollIntoView(posB, { y: 'end', yMargin: 20 })
                        });

                    }
                } catch (err) {
                    console.warn('Could not perform smart follow scroll:', err.message);
                }
            }

            function updateDocB(mergeView: MergeView, newContent: string): boolean {
                try {
                    // Validate inputs
                    if (!mergeView) {
                        console.error('MergeView is null or undefined');
                        return false;
                    }

                    const safeContent = ensureString(newContent, 'updateDocB newContent');

                    // Try to access the editor for doc B directly through the mergeView object
                    if (!mergeView.b || !mergeView.b.state) {
                        console.error('Could not access state for doc B');
                        return false;
                    }

                    // Get the current state and create a new state with the updated content
                    const currentState = mergeView.b.state;

                    if (!currentState.doc) {
                        console.error('Current state doc is null or undefined');
                        return false;
                    }


                    // Create a transaction to replace the entire document content
                    mergeView.b.dispatch({
                        changes: {
                            from: 0,
                            to: currentState.doc.length,
                            insert: safeContent
                        }
                    });

                    return true;
                } catch (err) {
                    console.error('Error updating doc B:', {
                        error: err.message,
                        stack: err.stack,
                        mergeViewExists: !!mergeView,
                        newContentType: typeof newContent
                    });
                    return false;
                }
            }




            const applySyntaxHighlighting = (mergeView) => {
                try {
                    const editors = mergeView.dom.querySelectorAll('.cm-editor');
                    console.log(`Found ${editors.length} editors in merge view`);

                    editors.forEach((editorElement, index) => {
                        const editorView = (editorElement as any).view;
                        if (editorView) {
                            debugEditorState(editorView, `Editor ${index}`);

                            // Add a class to the editor element based on file extension
                            const fileExtension = filePath.split('.').pop()?.toLowerCase() || '';
                            editorElement.classList.add(`language-${fileExtension}`);

                            // Force a refresh of the editor view using requestAnimationFrame for better performance
                            requestAnimationFrame(() => {
                                try {
                                    // Dispatch a dummy transaction to force a refresh
                                    editorView.dispatch({});
                                } catch (err) {
                                    console.error(`Error refreshing editor ${index}:`, err);
                                }
                            });
                        } else {
                            console.log(`Could not access view for editor ${index}`);
                        }
                    });
                } catch (err) {
                    console.error("Error applying syntax highlighting:", err);
                }
            };



            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }

            const { contents } = app.serviceManager;
            const { filePath, search, replace } = args;

            if ((search == undefined) || (replace == undefined)) {
                return ""
            }

            try {
                // CORRECT STREAMING APPROACH: Always apply diffs to original content, discard results during streaming
                let originalFileContent: string;
                let diffResult: string;
                let changePosition: { line: number, ch: number } | undefined;

                if (fileBaselines.has(filePath)) {
                    // Use cached baseline content (never changes)
                    originalFileContent = fileBaselines.get(filePath);
                } else {
                    // Read from model only for the very first operation
                    try {
                        originalFileContent = await getTextContentFromModel(filePath);

                        // Store as permanent baseline (never modified)
                        fileBaselines.set(filePath, originalFileContent);
                        streamingCallIds.set(filePath, call_id);
                    } catch (err) {
                        console.error(`Model content read failed for ${filePath}:`, err.message);
                        return JSON.stringify({
                            "status": "fail",
                            "message": `Cannot read file content: ${filePath} - ${err.message}`,
                            "stack": err.stack
                        });
                    }
                }

                // ALWAYS apply diff to original content (for display only during streaming)
                try {
                    // Apply diff to original content for display
                    const replaceResult = safeStringReplace(originalFileContent, search, replace, `${filePath} (display diff)`);
                    diffResult = replaceResult.result;
                    changePosition = replaceResult.changePosition;
                } catch (err) {
                    console.error(`❌ Failed to apply diff for ${filePath}:`, err.message);
                    return JSON.stringify({
                        "status": "fail",
                        "message": `Failed to apply diff for ${filePath}: ${err.message}`,
                        "stack": err.stack
                    });
                }

                if (mergeViews[call_id] != undefined) {
                    // Subsequent streaming updates - update content and smart follow scroll
                    updateDocB(mergeViews[call_id], diffResult);

                    // Apply smart follow scrolling for consecutive chunks
                    if (changePosition && streaming) {
                        // Use requestAnimationFrame to ensure content update is rendered first
                        requestAnimationFrame(() => {
                            smartFollowScroll(mergeViews[call_id], changePosition);
                        });
                    }
                } else if (mergeViews[call_id] == undefined) {

                    // Create a container for the merge view
                    const container = document.createElement('div');
                    container.style.height = '100%';
                    container.style.overflow = 'auto';

                    // Get language extensions for the file and add JupyterLab theme
                    const languageExtensions = [jupyterTheme, ...getLanguageExtensionsForFile(filePath)];

                    // Add a style element for syntax highlighting using JupyterLab's CSS variables
                    const styleElement = document.createElement('style');
                    styleElement.textContent = `
                        /* Basic syntax highlighting styles using JupyterLab variables */
                        .cm-keyword { color: var(--jp-mirror-editor-keyword-color); font-weight: bold; }
                        .cm-comment { color: var(--jp-mirror-editor-comment-color); }
                        .cm-string { color: var(--jp-mirror-editor-string-color); }
                        .cm-number { color: var(--jp-mirror-editor-number-color); }
                        .cm-operator { color: var(--jp-mirror-editor-operator-color); }
                        .cm-property { color: var(--jp-mirror-editor-property-color); }
                        .cm-variable { color: var(--jp-mirror-editor-variable-color); }
                        .cm-function, .cm-def { color: var(--jp-mirror-editor-def-color); }
                        .cm-atom { color: var(--jp-mirror-editor-atom-color); }
                        .cm-meta { color: var(--jp-mirror-editor-meta-color); }
                        .cm-tag { color: var(--jp-mirror-editor-tag-color); }
                        .cm-attribute { color: var(--jp-mirror-editor-attribute-color); }
                        .cm-qualifier { color: var(--jp-mirror-editor-qualifier-color); }
                        .cm-bracket { color: var(--jp-mirror-editor-bracket-color); }
                        .cm-builtin { color: var(--jp-mirror-editor-builtin-color); }
                        .cm-special { color: var(--jp-mirror-editor-string-2-color); }
    `;
                    document.head.appendChild(styleElement);

                    let mergeView: MergeView;
                    try {
                        mergeView = createMergeViewSafely(originalFileContent, diffResult, languageExtensions, filePath);
                    } catch (err) {
                        console.error(`MergeView creation failed for ${filePath}:`, {
                            error: err.message,
                            stack: err.stack
                        });
                        return JSON.stringify({
                            "status": "fail",
                            "message": `MergeView creation failed for ${filePath}: ${err.message}`,
                            "stack": err.stack
                        });
                    }


                    mergeViews[call_id] = mergeView;

                    container.appendChild(mergeView.dom);

                    // Apply syntax highlighting and scroll to change position on first creation
                    requestAnimationFrame(() => {
                        applySyntaxHighlighting(mergeView);

                        // Scroll to change position only on first chunk (MergeView creation)
                        if (changePosition) {
                            scrollToChangeOnce(mergeView, changePosition);
                        }
                    });

                    // Create a widget to hold the container
                    const widget = new Widget();
                    mergeWidgets[call_id] = widget;

                    widget.id = call_id;
                    widget.title.label = `Merge View: ${filePath} `;
                    widget.title.closable = true;
                    widget.node.appendChild(container);

                    // Add the widget to the main area and activate it
                    app.shell.add(widget, 'main');
                    app.shell.activateById(widget.id);

                }

                if (!streaming) {
                    // Clean up streaming cache when operation completes
                    fileBaselines.delete(filePath);
                    streamingCallIds.delete(filePath);
                    console.log(`🧹 Cleaned up streaming cache for ${filePath}`);

                    // Use model-based save approach
                    try {
                        const context = findDocumentContext(filePath);
                        console.log(`🎯 Found document context via open widget for ${filePath}`);

                        // Update model content and save
                        const modelState = {
                            isDirty: context.model.dirty,
                            contentLength: context.model.value?.text?.length || 0,
                            modelType: typeof context.model,
                            isReady: context.model.ready ? 'ready' : 'not ready'
                        };
                        console.log(`📊 Model state before update:`, modelState);

                        // Show content preview for debugging
                        const originalContent = context.model.value?.text || context.model.toString?.() || '';
                        console.log(`🔍 Original content preview:`, originalContent.substring(0, 100) + '...');

                        // Update the model content using the universal save method
                        await saveTextContentToModel(context, diffResult, filePath);

                        // Log updated state
                        const updatedModelState = {
                            isDirty: context.model.dirty,
                            contentLength: context.model.value?.text?.length || 0,
                            newContentLength: diffResult.length,
                            contentActuallyChanged: originalContent !== diffResult
                        };
                        console.log(`📊 Model state after update:`, updatedModelState);

                        // Show updated content preview
                        const updatedContent = context.model.value?.text || context.model.toString?.() || '';
                        console.log(`🔍 Updated content preview:`, updatedContent.substring(0, 100) + '...');

                        // Attempt to save the context
                        console.log(`💾 Attempting context save for ${filePath}...`);
                        await context.save();

                        const finalModelState = {
                            isDirty: context.model.dirty,
                            isReady: context.model.ready ? 'ready' : 'not ready',
                            path: context.path,
                            contentLength: context.model.value?.text?.length || 0
                        };
                        console.log(`📊 Model state after save:`, finalModelState);

                        console.log(`✅ File saved successfully via document context: ${filePath}`);
                    } catch (err) {
                        console.error(`❌ Model-based save failed for ${filePath}:`, err.message);
                        throw err;
                    }

                    // Close the diff view and open/focus the file
                    if (mergeViews[call_id]) {
                        const widget = mergeWidgets[call_id];
                        if (widget) {
                            // Close the diff view
                            widget.close();
                            console.log(`�️ Closed diff view for ${filePath}`);

                            // Open the file (or focus if already open)
                            try {
                                await app.commands.execute('docmanager:open', { path: filePath });
                                console.log(`📂 Opened/focused file: ${filePath}`);
                            } catch (err) {
                                console.warn(`Could not open file: ${err.message}`);
                            }
                        }
                    }

                    return JSON.stringify({
                        "status": "ok",
                        "new_content": diffResult
                    });

                }


            } catch (err) {
                return JSON.stringify({
                    "status": "fail",
                    "message": `Failed to open merge view: ${err.message} `,
                    "stack": err.stack
                });
            }
        }
    }
}
