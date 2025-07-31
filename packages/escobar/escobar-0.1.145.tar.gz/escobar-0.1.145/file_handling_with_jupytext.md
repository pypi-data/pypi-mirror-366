# File Handling in the Presence of Jupytext

## Introduction

Jupytext is a Jupyter ecosystem tool that enables notebooks to be represented as plain text files (such as `.py`, `.md`, `.Rmd`, etc.), allowing for version control, diffs, and collaborative workflows that are difficult with raw `.ipynb` files. For JupyterLab extensions and automation tools, understanding how to handle files in the presence (or absence) of Jupytext is critical for robust, user-friendly behavior.

---

## The Jupytext Workflow

When Jupytext is enabled, notebooks can be saved and opened as text files. This means:
- The notebook's content is stored in a human-readable format.
- Standard text editing, diffing, and merging tools can be used.
- The JupyterLab document model exposes these files as text models, not as JSON notebook models.

---

## Diff and Save Logic

### Supported Operations

- **Text-based notebooks (`.py`, `.md`, etc.)**:  
  - Read content using `model.toString()` or `model.value.text`.
  - Save content using `model.fromString(content)` or by setting `model.value.text = content`, then calling `context.save()`.
  - These operations are safe and robust for Jupytext-managed files.

**Example: Reading and Saving a Jupytext-Managed File in a JupyterLab Extension (TypeScript)**
```typescript
// Reading content
const content = typeof model.toString === 'function'
  ? model.toString()
  : model.value?.text;

// Saving content
if (typeof model.fromString === 'function') {
  model.fromString(newContent);
} else if (model.value?.text !== undefined) {
  model.value.text = newContent;
}
await context.save();
```

- **Raw `.ipynb` notebooks**:  
  - Direct editing or saving is **not supported** in this workflow.
  - Attempting to operate on `.ipynb` files should result in a clear error, instructing the user to use Jupytext to convert the notebook to a text format first.

**Example: Rejecting Direct `.ipynb` Handling**
```typescript
if (filePath.endsWith('.ipynb')) {
  throw new Error('Cannot edit .ipynb files directly. Use Jupytext to convert to text format first.');
}
```

### Why Not Edit `.ipynb` Directly?

- The `.ipynb` format is a complex JSON structure, prone to corruption if not handled carefully.
- Diffs and merges on JSON are error-prone and not user-friendly.
- Jupytext solves these issues by providing a text-based representation.

---

## Consistency and Safety

- **With Jupytext present**:  
  - All notebook operations should target the text-based representation.
  - The extension should refuse to operate on `.ipynb` files directly.

- **Without Jupytext**:  
  - Only plain text files are supported.
  - Attempting to operate on `.ipynb` files should result in an error.

- **Error Handling**:  
  - Always provide clear feedback if an operation is not supported (e.g., "Cannot edit .ipynb files directly. Use Jupytext to convert to text format first.").

---

## Best Practices and Recommendations

- Always check the file extension before performing diff or save operations.
- Use the JupyterLab document model's text methods for Jupytext-managed files.
- Never attempt to patch or manipulate `.ipynb` files as plain text.
- Encourage users to open files in JupyterLab before performing automated operations, as context discovery relies on open widgets.

**Example: Checking File Extension Before Operation**
```typescript
function isJupytextFile(filePath: string): boolean {
  return /\.(py|md|Rmd|txt|jl|cpp|c|r|sh|q|scala|rs|pl|js|ts|json)$/.test(filePath);
}

if (!isJupytextFile(filePath)) {
  throw new Error('Only Jupytext text files are supported for this operation.');
}
```

---

## Supported Operations Table

| File Type         | Jupytext Present | Jupytext Absent | Behavior                                      |
|-------------------|------------------|-----------------|-----------------------------------------------|
| `.py`, `.md` etc. | Yes              | Yes             | Diff/save works (text model)                  |
| `.ipynb`          | Yes              | No              | Error: must use Jupytext text format          |
| `.ipynb`          | No               | No              | Error: must use Jupytext text format          |

---

## Conclusion

Handling files in the presence of Jupytext requires a text-centric approach. By refusing to operate on raw `.ipynb` files and leveraging the JupyterLab document model for text-based notebooks, extensions and tools can provide robust, user-friendly, and version-control-friendly workflows. Always encourage users to use Jupytext for collaborative and automated notebook operations.
