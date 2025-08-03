import { VERSION } from '../version';

/**
 * Interface for tool information
 */
export interface IToolInfo {
    name: string;
    description: string;
    enabled?: boolean;
}

/**
 * Tools selection page for managing which tools the LLM can access
 */
export class ToolsSelectionPage {
    private container: HTMLDivElement;
    private overlay: HTMLDivElement;
    private tools: IToolInfo[];
    private onSave: (enabledTools: string[]) => void;
    private contentContainer: HTMLDivElement;
    private isLoading: boolean = false;

    /**
     * Create a new ToolsSelectionPage
     * @param tools Array of available tools
     * @param enabledTools Array of currently enabled tool names
     * @param onSave Callback function when tools selection is saved
     */
    constructor(
        tools: IToolInfo[],
        enabledTools: string[] = [],
        onSave: (enabledTools: string[]) => void
    ) {
        // Map tools with enabled state (default ON unless explicitly disabled)
        this.tools = tools.map(tool => ({
            ...tool,
            enabled: enabledTools.includes(tool.name)
        }));

        this.onSave = onSave;

        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'escobar-settings-overlay';
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.hide();
            }
        });

        // Create container
        this.container = this.createContainer();
        this.overlay.appendChild(this.container);

        // Listen for tools updates
        this.setupToolsListener();
    }

    /**
     * Set up listener for tools updates
     */
    private setupToolsListener(): void {
        // Listen for tools updates from the global window object
        const checkForToolsUpdates = () => {
            const availableTools = (window as any).escobarAvailableTools as IToolInfo[] || [];
            if (availableTools.length > 0 && availableTools.length !== this.tools.length) {
                this.updateTools(availableTools);
            }
        };

        // Check periodically for tools updates
        setInterval(checkForToolsUpdates, 1000);
    }

    /**
     * Update tools and refresh the modal content
     */
    private updateTools(newTools: IToolInfo[]): void {
        // Get currently enabled tools from settings using new JSON format
        const currentSettings = (window as any).escobarCurrentSettings || {};
        const toolsConfigStr = currentSettings.toolsConfig || '{}';

        let toolsConfig;
        try {
            toolsConfig = JSON.parse(toolsConfigStr);
        } catch (error) {
            toolsConfig = {};
        }

        const endpoints = toolsConfig.endpoints || {};

        // Update tools with enabled state (default ON unless explicitly disabled)
        this.tools = newTools.map(tool => ({
            ...tool,
            enabled: endpoints[tool.name] !== false  // Default to true unless explicitly false
        }));

        // Refresh the content
        this.refreshContent();
    }

    /**
     * Refresh the modal content
     */
    private refreshContent(): void {
        // Find the form and replace its content
        const form = this.container.querySelector('.escobar-settings-form') as HTMLFormElement;
        if (form) {
            // Clear existing content except header
            const formElements = form.querySelectorAll('.escobar-tools-description, .escobar-tool-group, .escobar-settings-buttons, .escobar-tools-loading, .escobar-tools-empty');
            formElements.forEach(element => element.remove());

            // Re-add description
            const description = this.createDescription();
            form.appendChild(description);

            // Re-add tools or appropriate message
            this.addToolsContent(form);

            // Re-add buttons
            const buttonsContainer = this.createButtonsContainer();
            form.appendChild(buttonsContainer);
        }
    }

    /**
     * Create the tools selection UI container
     */
    private createContainer(): HTMLDivElement {
        // Create container
        const container = document.createElement('div');
        container.className = 'escobar-settings-container';
        container.style.maxWidth = '500px';

        // Create header
        const header = this.createHeader();
        container.appendChild(header);

        // Add tools indicator
        const toolsIndicator = document.createElement('div');
        toolsIndicator.className = 'escobar-mode-indicator';
        toolsIndicator.innerHTML = `Available Tools <span style="font-size: 0.8em; opacity: 0.8;">v${VERSION}</span>`;
        toolsIndicator.style.backgroundColor = '#f0f8ff';
        toolsIndicator.style.color = '#1e40af';
        toolsIndicator.style.padding = '8px 16px';
        toolsIndicator.style.margin = '0 16px 16px 16px';
        toolsIndicator.style.borderRadius = '4px';
        toolsIndicator.style.fontWeight = 'bold';
        toolsIndicator.style.textAlign = 'center';
        toolsIndicator.style.border = '1px solid #bfdbfe';
        container.appendChild(toolsIndicator);

        // Create form
        const form = document.createElement('form');
        form.className = 'escobar-settings-form';
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveSettings();
        });

        // Add description
        const description = this.createDescription();
        form.appendChild(description);

        // Add tools content
        this.addToolsContent(form);

        // Create buttons
        const buttonsContainer = this.createButtonsContainer();
        form.appendChild(buttonsContainer);

        container.appendChild(form);

        return container;
    }

    /**
     * Create description section
     */
    private createDescription(): HTMLDivElement {
        const description = document.createElement('div');
        description.className = 'escobar-tools-description';
        description.style.cssText = `
      margin: 0 16px 16px 16px;
      padding: 12px;
      background: var(--jp-layout-color0);
      border: 1px solid var(--jp-border-color1);
      border-radius: 4px;
      font-size: 14px;
      color: var(--jp-content-font-color1);
    `;
        description.innerHTML = `
      <strong>Tool Selection</strong><br>
      Choose which tools the AI assistant can access during conversations. 
      Enabled tools will be available for the LLM to use when responding to your requests.
    `;
        return description;
    }

    /**
     * Add tools content to the form
     */
    private addToolsContent(form: HTMLFormElement): void {
        if (this.tools.length === 0) {
            // Check if tools are available globally but weren't passed to constructor
            const availableTools = (window as any).escobarAvailableTools as IToolInfo[] || [];

            if (availableTools.length > 0) {
                // Tools are available globally, update our instance
                this.updateTools(availableTools);
                return; // updateTools will call refreshContent which will call this method again
            } else {
                // No tools available anywhere, show waiting message
                const waitingMessage = this.createWaitingMessage();
                form.appendChild(waitingMessage);
            }
        } else {
            // Show tools that were passed to constructor or loaded later
            this.tools.forEach(tool => {
                const toolGroup = this.createToolToggle(tool);
                form.appendChild(toolGroup);
            });
        }
    }

    /**
     * Create waiting message for when tools are loading
     */
    private createWaitingMessage(): HTMLDivElement {
        const waitingMessage = document.createElement('div');
        waitingMessage.className = 'escobar-tools-loading';
        waitingMessage.style.cssText = `
        margin: 16px;
        padding: 20px;
        text-align: center;
        color: var(--jp-content-font-color2);
        background: var(--jp-layout-color1);
        border: 1px solid var(--jp-border-color1);
        border-radius: 6px;
      `;

        waitingMessage.innerHTML = `
        <div style="margin-bottom: 12px;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite;">
            <path d="M21 12a9 9 0 11-6.219-8.56"/>
          </svg>
        </div>
        <div style="font-weight: bold; margin-bottom: 8px;">Loading Tools...</div>
        <div style="font-size: 13px; opacity: 0.8;">
          Tools will appear here after the connection is established and chat list is loaded.
        </div>
        <button type="button" style="
          margin-top: 12px;
          padding: 6px 12px;
          background: var(--jp-brand-color1);
          color: var(--jp-ui-inverse-font-color1);
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
        " onclick="this.parentElement.querySelector('svg').style.animation = 'spin 1s linear infinite';">
          Refresh
        </button>
        <style>
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        </style>
      `;

        // Add refresh functionality
        const refreshButton = waitingMessage.querySelector('button');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.checkForToolsAndRefresh();
            });
        }

        return waitingMessage;
    }

    /**
     * Create no tools message
     */
    private createNoToolsMessage(): HTMLDivElement {
        const noToolsMessage = document.createElement('div');
        noToolsMessage.className = 'escobar-tools-empty';
        noToolsMessage.style.cssText = `
        margin: 16px;
        padding: 20px;
        text-align: center;
        color: var(--jp-content-font-color2);
        background: var(--jp-layout-color1);
        border: 1px solid var(--jp-border-color1);
        border-radius: 6px;
      `;

        noToolsMessage.innerHTML = `
        <div style="font-weight: bold; margin-bottom: 8px;">No Tools Available</div>
        <div style="font-size: 13px; opacity: 0.8; margin-bottom: 12px;">
          The server hasn't provided any tools for selection.
        </div>
        <button type="button" style="
          padding: 6px 12px;
          background: var(--jp-brand-color1);
          color: var(--jp-ui-inverse-font-color1);
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
        ">
          Refresh
        </button>
      `;

        // Add refresh functionality
        const refreshButton = noToolsMessage.querySelector('button');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.checkForToolsAndRefresh();
            });
        }

        return noToolsMessage;
    }

    /**
     * Check for tools and refresh if found
     */
    private checkForToolsAndRefresh(): void {
        const availableTools = (window as any).escobarAvailableTools as IToolInfo[] || [];
        if (availableTools.length > 0) {
            this.updateTools(availableTools);
        } else {
            // Show loading state briefly
            const loadingElements = this.container.querySelectorAll('.escobar-tools-loading svg, .escobar-tools-empty');
            loadingElements.forEach(element => {
                if (element.tagName === 'svg') {
                    (element as SVGElement).style.animation = 'spin 1s linear infinite';
                }
            });

            // Check again after a short delay
            setTimeout(() => {
                const newAvailableTools = (window as any).escobarAvailableTools as IToolInfo[] || [];
                if (newAvailableTools.length > 0) {
                    this.updateTools(newAvailableTools);
                }
            }, 1000);
        }
    }

    /**
     * Create a header for the tools selection container
     */
    private createHeader(): HTMLDivElement {
        const header = document.createElement('div');
        header.className = 'escobar-settings-header';

        const titleElement = document.createElement('h2');
        titleElement.textContent = 'Tools Selection';
        header.appendChild(titleElement);

        const closeButton = document.createElement('button');
        closeButton.className = 'escobar-settings-close-button';
        closeButton.innerHTML = '&times;';
        closeButton.addEventListener('click', () => this.hide());
        header.appendChild(closeButton);

        return header;
    }

    /**
     * Create a toggle switch for a tool
     */
    private createToolToggle(tool: IToolInfo): HTMLDivElement {
        const group = document.createElement('div');
        group.className = 'escobar-settings-group escobar-tool-group';
        group.style.cssText = `
      margin: 0 16px 16px 16px;
      padding: 16px;
      border: 1px solid var(--jp-border-color1);
      border-radius: 6px;
      background: var(--jp-layout-color0);
    `;

        // Create toggle container
        const toggleContainer = document.createElement('div');
        toggleContainer.style.cssText = `
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
    `;

        // Tool name
        const toolName = document.createElement('div');
        toolName.style.cssText = `
      font-weight: bold;
      font-size: 16px;
      color: var(--jp-content-font-color1);
    `;
        toolName.textContent = tool.name;
        toggleContainer.appendChild(toolName);

        // Toggle switch
        const toggleSwitch = document.createElement('label');
        toggleSwitch.className = 'escobar-toggle-switch';
        toggleSwitch.style.cssText = `
      position: relative;
      display: inline-block;
      width: 50px;
      height: 24px;
      cursor: pointer;
    `;

        const toggleInput = document.createElement('input');
        toggleInput.type = 'checkbox';
        toggleInput.checked = tool.enabled || false;
        toggleInput.dataset.toolName = tool.name;
        toggleInput.style.cssText = `
      opacity: 0;
      width: 0;
      height: 0;
    `;

        const toggleSlider = document.createElement('span');
        toggleSlider.className = 'escobar-toggle-slider';
        toggleSlider.style.cssText = `
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #ccc;
      transition: .4s;
      border-radius: 24px;
    `;

        // Add the slider dot
        const sliderDot = document.createElement('span');
        sliderDot.style.cssText = `
      position: absolute;
      content: "";
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .4s;
      border-radius: 50%;
    `;
        toggleSlider.appendChild(sliderDot);

        // Update slider appearance based on checked state
        const updateSlider = () => {
            if (toggleInput.checked) {
                toggleSlider.style.backgroundColor = 'var(--jp-brand-color1)';
                sliderDot.style.transform = 'translateX(26px)';
            } else {
                toggleSlider.style.backgroundColor = '#ccc';
                sliderDot.style.transform = 'translateX(0)';
            }
        };

        // Initial update
        updateSlider();

        // Add change listener
        toggleInput.addEventListener('change', updateSlider);

        toggleSwitch.appendChild(toggleInput);
        toggleSwitch.appendChild(toggleSlider);
        toggleContainer.appendChild(toggleSwitch);

        group.appendChild(toggleContainer);

        // Tool description
        const toolDescription = document.createElement('div');
        toolDescription.style.cssText = `
      font-size: 14px;
      color: var(--jp-content-font-color2);
      line-height: 1.4;
    `;
        toolDescription.textContent = tool.description;
        group.appendChild(toolDescription);

        return group;
    }

    /**
     * Create buttons container with Save and Cancel buttons
     */
    private createButtonsContainer(): HTMLDivElement {
        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'escobar-settings-buttons';

        const cancelButton = document.createElement('button');
        cancelButton.className = 'escobar-settings-button escobar-settings-cancel-button';
        cancelButton.textContent = 'Cancel';
        cancelButton.type = 'button';
        cancelButton.addEventListener('click', () => this.hide());
        buttonsContainer.appendChild(cancelButton);

        const saveButton = document.createElement('button');
        saveButton.className = 'escobar-settings-button escobar-settings-save-button';
        saveButton.textContent = 'Save';
        saveButton.type = 'submit';
        buttonsContainer.appendChild(saveButton);

        return buttonsContainer;
    }

    /**
     * Show the tools selection page
     */
    public show(): void {
        document.body.appendChild(this.overlay);

        // Add animation class after a small delay to trigger animation
        setTimeout(() => {
            this.overlay.classList.add('escobar-settings-overlay-visible');
            this.container.classList.add('escobar-settings-container-visible');
        }, 10);
    }

    /**
     * Hide the tools selection page
     */
    public hide(): void {
        this.overlay.classList.remove('escobar-settings-overlay-visible');
        this.container.classList.remove('escobar-settings-container-visible');

        // Remove from DOM after animation completes
        setTimeout(() => {
            if (this.overlay.parentNode) {
                this.overlay.parentNode.removeChild(this.overlay);
            }
        }, 300); // Match the CSS transition duration
    }

    /**
     * Save tools selection
     */
    private saveSettings(): void {
        // Get all toggle inputs
        const toggleInputs = this.container.querySelectorAll('input[data-tool-name]') as NodeListOf<HTMLInputElement>;

        // Collect enabled tools
        const enabledTools: string[] = [];
        toggleInputs.forEach(input => {
            if (input.checked && input.dataset.toolName) {
                enabledTools.push(input.dataset.toolName);
            }
        });

        // Call the save callback
        this.onSave(enabledTools);

        // Hide the page
        this.hide();
    }
}

/**
 * Show tools selection modal
 * @param tools Array of available tools
 * @param enabledTools Array of currently enabled tool names
 * @param onSave Callback function when tools selection is saved
 */
export function showToolsSelection(
    tools: IToolInfo[],
    enabledTools: string[] = [],
    onSave: (enabledTools: string[]) => void
): void {
    const toolsPage = new ToolsSelectionPage(tools, enabledTools, onSave);
    toolsPage.show();
}
