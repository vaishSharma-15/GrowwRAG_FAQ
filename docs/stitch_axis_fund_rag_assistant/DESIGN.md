---
name: Financial Intelligence System
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#393939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#cac3d8'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#948ea1'
  outline-variant: '#494455'
  surface-tint: '#cdbdff'
  primary: '#cdbdff'
  on-primary: '#370096'
  primary-container: '#7c4dff'
  on-primary-container: '#fcf6ff'
  inverse-primary: '#6833ea'
  secondary: '#40e56c'
  on-secondary: '#003912'
  secondary-container: '#02c953'
  on-secondary-container: '#004d1b'
  tertiary: '#d4bbff'
  on-tertiary: '#400688'
  tertiary-container: '#855ace'
  on-tertiary-container: '#fdf6ff'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e8deff'
  primary-fixed-dim: '#cdbdff'
  on-primary-fixed: '#20005f'
  on-primary-fixed-variant: '#4f00d0'
  secondary-fixed: '#69ff87'
  secondary-fixed-dim: '#3ce36a'
  on-secondary-fixed: '#002108'
  on-secondary-fixed-variant: '#00531e'
  tertiary-fixed: '#ebdcff'
  tertiary-fixed-dim: '#d4bbff'
  on-tertiary-fixed: '#260058'
  on-tertiary-fixed-variant: '#582a9f'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-md:
    fontFamily: Hanken Grotesk
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-lg:
    fontFamily: Hanken Grotesk
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Hanken Grotesk
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Hanken Grotesk
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 48px
---

## Brand & Style

This design system is engineered for a high-stakes financial intelligence environment, prioritizing speed of cognition and executive-level aesthetics. The brand personality is authoritative yet visionary, moving away from traditional banking blues into a high-contrast, "cyber-premium" territory. 

The design style is **Modern Minimalist with Glassmorphic accents**. It utilizes a deep charcoal foundation to eliminate visual noise, allowing the vibrant purple and mint green to act as functional beacons for navigation and data interpretation. The aesthetic response should be one of "controlled power"—a system that feels both technically advanced and impeccably refined.

## Colors

The palette is anchored by a **Deep Charcoal (#0A0A0A)** background to ensure maximum contrast for data visualization. 

- **Primary Purple (#7C4DFF):** Used for the core brand identity, primary actions, active navigation states, and focus indicators.
- **Mint Green (#00C853):** Reserved exclusively for "positive" signals—upward market trends, successful transactions, "Verified" status badges, and completed states.
- **Accents:** A softer lavender (#B388FF) is used for secondary interactive elements or hover states to provide depth without breaking the monochromatic dark theme.
- **Neutrals:** Greyscale values are strictly controlled to maintain hierarchy, with primary text in pure white and metadata in a muted silver-grey.

## Typography

The system utilizes **Hanken Grotesk** exclusively to leverage its sharp, contemporary geometry and high legibility in data-dense environments. 

Headlines use tighter letter-spacing and heavier weights to create a sense of importance and "editorial" structure. Body text is optimized for long-form financial reports with generous line heights. Labels, particularly those used in data tables or status badges, utilize a slightly increased weight and uppercase styling for "label-sm" to ensure they are distinguishable even at small scales.

## Layout & Spacing

This design system follows a **Fixed-Fluid Hybrid Grid**. Content is housed within a 12-column system on desktop with a max-width of 1440px to maintain readability. 

- **Grid:** 24px gutters provide significant breathing room between complex data widgets.
- **Rhythm:** An 8px linear scale governs all padding and margins, ensuring a consistent vertical rhythm.
- **Responsive Behavior:** On mobile, the grid collapses to 4 columns with 16px side margins. Data tables reflow into card-based lists to maintain legibility of financial figures.

## Elevation & Depth

Depth is communicated through **Tonal Layering** and **Subtle Glassmorphism** rather than traditional heavy shadows.

- **Level 0 (Background):** Pure charcoal (#0A0A0A).
- **Level 1 (Cards/Widgets):** Surface color (#1E1E1E) with a subtle 1px border (#2E2E2E).
- **Level 2 (Overlays/Modals):** A semi-transparent surface with a 20px backdrop blur and a very faint purple-tinted stroke (10% opacity of #7C4DFF).
- **Interactions:** Hover states on interactive elements should trigger a "glow" effect—a soft, diffused outer shadow using the primary purple color at 20% opacity.

## Shapes

The system adopts a **Soft (0.25rem)** rounding strategy. This provides a professional, "tooled" look that feels engineered rather than organic. 

- **Small Components:** Checkboxes and small tags use 4px (0.25rem) radii.
- **Medium Components:** Buttons and input fields use 8px (0.5rem) radii.
- **Large Components:** Dashboard cards and modals use 12px (0.75rem) radii to soften the overall interface without losing the "Financial Intelligence" precision.

## Components

- **Buttons:** Primary buttons are solid Purple (#7C4DFF) with white text. Secondary buttons use a ghost style with a Purple stroke. "Success" actions (e.g., Approve) use a Mint Green (#00C853) solid fill.
- **Verified Badges:** Small, pill-shaped tags with a Mint Green background (15% opacity), Mint Green text, and a leading checkmark icon.
- **Input Fields:** Dark backgrounds (#121212) with a 1px border that turns Purple (#7C4DFF) on focus. Labels sit strictly above the field.
- **Data Visualizations:** Positive trends must use Mint Green. Neutral or structural lines use Lavender. Negative trends (if required) should use a muted grey/white or a very desaturated slate—avoiding red as per the specific brand directive.
- **Navigation:** The active state in the sidebar or top nav is indicated by a vertical/horizontal "power bar" in Purple (#7C4DFF) and a slight lightening of the background.
- **Cards:** Content is segmented using subtle dividers (#2E2E2E) rather than nesting cards within cards.