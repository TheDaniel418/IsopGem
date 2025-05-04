# PyCharm AI Assistant Configuration

This directory contains configuration and resources for optimizing the PyCharm AI Assistant experience with IsopGem.

## Directory Structure

- `modes/` - Contains mode-specific rule files that tailor the AI's behavior for different tasks
- `mode_activator.md` - Instructions for activating different AI modes

## Using AI Modes

The AI Assistant supports different modes of operation that optimize its responses for specific tasks:

1. To activate a mode, start your message with the mode indicator in square brackets:
   ```
   [CODE] Please implement a function to calculate gematria values
   ```

2. Each mode has specific rules and response structures optimized for that task type

3. View the `mode_activator.md` file for a quick reference of available modes

## IsopGem-Specific Knowledge

The AI Assistant has been configured with knowledge about IsopGem's:

1. **Five-Pillar Architecture**
   - Gematria
   - Geometry
   - Document Manager
   - Astrology
   - TQ (Trigrammaton QBLH)

2. **Component Structure** for each pillar:
   - UI (User Interface)
   - Services (Business Logic)
   - Models (Data Structures)
   - Repositories (Data Access)
   - Utils (Helper Functions)

3. **Project Standards**
   - Coding conventions
   - Documentation requirements
   - Testing approaches

## Customizing AI Behavior

To customize the AI Assistant's behavior:

1. Modify existing mode files in the `modes/` directory
2. Create new mode files following the established format
3. Update references in the README and mode_activator files

## Best Practices

1. **Be Specific** with your requests
2. **Use the Right Mode** for your task
3. **Provide Context** when needed
4. **Give Feedback** to improve responses
