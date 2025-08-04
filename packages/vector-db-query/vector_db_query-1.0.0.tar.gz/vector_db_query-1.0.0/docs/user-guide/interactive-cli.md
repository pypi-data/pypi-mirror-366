# Interactive CLI Guide

The interactive CLI provides a rich terminal interface for Vector DB Query with advanced features and beautiful visualizations.

## Starting Interactive Mode

```bash
# Start with default settings
vector-db-query interactive start

# Start with specific theme
vector-db-query interactive start --theme monokai

# Start in specific mode
vector-db-query interactive menu
vector-db-query interactive browse
vector-db-query interactive query
```

## Main Features

### 1. Main Menu

The main menu is your starting point:

- **Process Documents** - Index new files
- **Query Database** - Search your documents  
- **Browse Documents** - View indexed content
- **MCP Server** - Manage AI integration
- **Settings** - Configure the application
- **System Status** - View statistics
- **Help & Tutorials** - Learn features

Navigate with:
- ↑/↓ arrows - Move selection
- Enter - Select option
- Esc - Go back
- q - Quit application

### 2. File Browser

Advanced file navigation:

```
┌─ File Browser ─────────────────────────┐
│ 📁 Documents/                          │
│   📁 Projects/                         │
│   📁 Research/                         │
│   📄 report.pdf (2.3 MB)              │
│   📄 notes.md (15 KB)                 │
│                                        │
│ [Space: Select] [Enter: Process]       │
└────────────────────────────────────────┘
```

Features:
- **Preview** - View file contents before processing
- **Multi-select** - Process multiple files at once
- **Filtering** - Show only specific file types
- **Sorting** - By name, size, or date
- **Search** - Find files by name

Keyboard shortcuts:
- Space - Toggle selection
- a - Select all
- i - Invert selection
- p - Preview file
- f - Filter files
- / - Search

### 3. Query Builder

Interactive query construction:

```
┌─ Query Builder ────────────────────────┐
│ Query: machine learning algorithms     │
│                                        │
│ 🔍 Suggestions:                        │
│ • "deep learning techniques"           │
│ • "ML algorithm comparison"            │
│ • "supervised learning methods"        │
│                                        │
│ Recent Queries:                        │
│ • "neural networks"                    │
│ • "data preprocessing"                 │
└────────────────────────────────────────┘
```

Features:
- **Auto-complete** - Smart suggestions as you type
- **Query history** - Access previous searches
- **Templates** - Pre-built query patterns
- **Advanced mode** - Add filters and operators

Shortcuts:
- Tab - Auto-complete
- ↑/↓ - Browse history
- Ctrl+T - Insert template
- Ctrl+F - Add filter

### 4. Result Viewer

Beautiful result display:

```
┌─ Search Results ───────────────────────┐
│ Query: "Python async programming"      │
│ Found: 15 results                      │
│                                        │
│ 1. async_guide.md (Score: 0.95)       │
│    ...Python's async/await syntax...   │
│                                        │
│ 2. concurrency.pdf (Score: 0.89)      │
│    ...concurrent programming...        │
│                                        │
│ [Enter: View] [E: Export] [N: Next]   │
└────────────────────────────────────────┘
```

Features:
- **Syntax highlighting** - Colored code snippets
- **Score display** - Relevance indicators
- **Pagination** - Navigate large result sets
- **Export** - Save results to file
- **Quick actions** - Open source files

Controls:
- Enter - View full result
- e - Export results
- o - Open source file
- n/p - Next/previous page
- 1-9 - Jump to result

## Advanced Features

### Keyboard Navigation

Global shortcuts available everywhere:

- **Ctrl+C** - Exit application
- **Ctrl+L** - Clear screen
- **F1** - Show help
- **F5** - Refresh
- **Ctrl+S** - Save state

Context-specific shortcuts:
- **?** - Show current shortcuts
- **h** - Context help
- **/** - Quick search
- **:** - Command mode

### Preferences

Customize your experience:

```bash
# Open preferences editor
vector-db-query interactive config
```

Available preferences:
- **Theme** - Color schemes (monokai, dracula, nord, etc.)
- **Animations** - Enable/disable animations
- **Icons** - Show/hide icons
- **Layout** - Compact or spacious
- **Shortcuts** - Customize key bindings

### Tutorials

Interactive tutorials guide you through features:

1. **Getting Started** - Basic navigation
2. **File Processing** - Document indexing
3. **Query Mastery** - Advanced search
4. **Customization** - Personalization
5. **MCP Setup** - AI integration

Access tutorials:
- From main menu → Help & Tutorials
- Press F1 then select "Tutorials"
- Run: `vector-db-query tutorial`

## Performance Features

### Progress Tracking

Real-time progress for long operations:

```
Processing Documents
├─ Reading files       ████████████ 100%
├─ Creating chunks     ████████░░░░  75%
├─ Generating vectors  ████░░░░░░░░  35%
└─ Storing in DB       ░░░░░░░░░░░░   0%

Time elapsed: 00:02:34
Files processed: 45/120
```

### Caching

Smart caching improves performance:
- Recent queries cached
- File previews cached
- Navigation history preserved

### Batch Operations

Process multiple items efficiently:
- Select multiple files
- Bulk status updates
- Parallel processing

## Customization

### Themes

Built-in themes:
- **Monokai** - Classic dark theme
- **Dracula** - Popular dark theme
- **Nord** - Nordic-inspired colors
- **Solarized** - Balanced contrast
- **One Dark** - Atom-inspired

Apply theme:
```bash
vector-db-query config set theme dracula
```

### Custom Shortcuts

Define your own shortcuts:

```yaml
# ~/.vector_db_query/shortcuts.yaml
shortcuts:
  ctrl+p: process_current_dir
  ctrl+q: quick_query
  alt+1: switch_to_tab_1
```

### Layouts

Choose layout style:
- **Compact** - Maximum information density
- **Normal** - Balanced spacing
- **Spacious** - Comfortable reading

## Tips and Tricks

### Efficiency Tips

1. **Use keyboard shortcuts** - Faster than mouse
2. **Enable type-ahead** - Find options quickly  
3. **Create query templates** - Reuse common searches
4. **Batch operations** - Process multiple files

### Power User Features

1. **Command mode** - Press `:` for commands
   - `:process ~/docs` - Quick process
   - `:query machine learning` - Quick search
   - `:set theme nord` - Change settings

2. **Macros** - Record and replay actions
   - Ctrl+Q - Start recording
   - Ctrl+Q - Stop recording
   - Ctrl+P - Play macro

3. **Split views** - Work with multiple panels
   - Ctrl+| - Vertical split
   - Ctrl+- - Horizontal split
   - Ctrl+W - Switch panels

### Troubleshooting

Common issues and solutions:

**Slow rendering**
- Disable animations: `set animations false`
- Use simpler theme: `set theme simple`

**Key conflicts**
- Check terminal settings
- Remap conflicting shortcuts

**Display issues**
- Ensure terminal supports Unicode
- Try different terminal emulator

## Integration

### Terminal Integration

Works best with:
- **iTerm2** (macOS) - Full feature support
- **Windows Terminal** - Modern Windows option
- **Alacritty** - Fast and minimal
- **Kitty** - GPU-accelerated

### Shell Integration

Add to your shell profile:

```bash
# Bash/Zsh alias
alias vdq='vector-db-query interactive start'

# Quick search function
vdq-search() {
    vector-db-query query "$@"
}
```

## Next Steps

- Learn about [Document Processing](document-processing.md)
- Master [Search and Query](search-query.md)
- Configure [MCP Integration](mcp-integration.md)
- Optimize [Performance](performance.md)