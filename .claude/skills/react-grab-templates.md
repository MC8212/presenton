---
description: Template refinement workflow using react-grab. Use when refining presentation templates, debugging template rendering, or creating new templates with live UI context.
---

# React-Grab Template Refinement Skill

This skill provides guided workflows for refining, debugging, and creating Presenton presentation templates using react-grab's point-and-click element capture.

## Prerequisites

Start the development server with react-grab enabled:

```bash
cd servers/nextjs
npm run dev:grab
```

This runs both the Next.js dev server and the @react-grab/claude-code server (port 4567) concurrently.

## How React-Grab Works

1. Navigate to `/custom-template` or `/template-preview` in your browser
2. Hold **⌘** (Mac) or **Ctrl** (Windows) and click on any element
3. React-grab captures and sends to Claude Code:
   - Component file path
   - React component name
   - HTML markup
   - CSS classes (Tailwind)

## Workflows

### Refining an Existing Template

1. Navigate to `/template-preview/{template-id}` in browser
2. Find the slide element you want to refine
3. ⌘+Click on the element
4. Tell me what changes you want:
   - "Fix the text alignment in this element"
   - "Make the background darker"
   - "Increase the font size of the title"

### Debugging Template Rendering Issues

1. Navigate to the page showing the broken template
2. ⌘+Click on the problematic element
3. Describe the issue:
   - "This element is overflowing its container"
   - "The colors don't match the design"
   - "The spacing is wrong"

### Creating New Templates from Reference

1. Navigate to `/template-preview` to see all templates
2. ⌘+Click on elements you want to use as reference
3. Describe the new template:
   - "Create a new intro slide based on this layout but with NH branding"
   - "Make a metrics slide similar to this but with 4 columns instead of 3"

## Template File Locations

| Type | Location |
|------|----------|
| Built-in templates | `servers/nextjs/presentation-templates/{theme}/` |
| Custom templates | Database (`PresentationLayoutCodeModel`) |
| NH-branded templates | `servers/nextjs/presentation-templates/nh-*/` |

## Common Refinement Tasks

### Fix Layout Issues
After capturing with react-grab, ask:
- "The captured element has misaligned text. Fix the Tailwind classes."
- "The flex container isn't centering properly."
- "The grid layout breaks on smaller aspect ratios."

### Apply NH Brand Colors
```
"Update the captured component to use NH brand colors:
- Primary: #00416A (navy)
- Secondary: #E87722 (orange)
- Accent: #4CAF50 (green)
- Text: #333333
- Background: #F5F5F5"
```

### Add Animation
- "Add a subtle fade-in animation to this slide layout."
- "Make the title slide in from the left."
- "Add a scale effect on hover for this card."

### Improve Typography
- "Increase the heading size and add more contrast."
- "Use the NH brand font family."
- "Fix the line height for better readability."

### Adjust Spacing
- "Add more padding around the content area."
- "Reduce the gap between cards."
- "Make the margins consistent with other slides."

## Template Architecture Context

When working with templates, keep in mind:

1. **Slide layouts are React components** that receive a `data` prop with slide content
2. **Schemas are defined with Zod** to validate and type the data structure
3. **Templates use Tailwind CSS** for styling (not CSS modules)
4. **Aspect ratio is typically 16:9** (1920x1080 equivalent)
5. **Custom templates are stored in the database** and compiled at runtime

## Tips for Effective Refinement

1. **Capture the specific element** - Click on the exact element you want to modify, not its parent
2. **Be specific about changes** - "Make text bigger" vs "Change text from text-lg to text-2xl"
3. **Test at different scales** - Templates render at various sizes (preview, edit, export)
4. **Keep accessibility in mind** - Ensure sufficient color contrast and readable fonts
