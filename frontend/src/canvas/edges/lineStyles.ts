import type { LineType } from '@/schema';

/**
 * Single source of truth for how each connection (edge) line type is drawn.
 * Both the pipe renderer (`PipeEdge.vue`) and the Legend tab read from here so
 * the canvas and its legend can never drift apart.
 *
 * The styling follows ISA-5.1 signal-line conventions in spirit: the main
 * process/piping run is a solid heavy line, and the various instrument signals
 * are lighter lines distinguished by their dash pattern.
 */
export interface LineStyle {
  /** Human label shown in the legend and inspector. */
  label: string;
  /** What this line type represents. */
  description: string;
  /** SVG `stroke-dasharray`; omit for a solid line. */
  dash?: string;
  /** Stroke width in px. */
  width: number;
}

export const LINE_STYLES: Record<LineType, LineStyle> = {
  process: {
    label: 'Process',
    description: 'Main piping — material flow (product, feed, utility fluids).',
    width: 2.5,
  },
  signal: {
    label: 'Instrument signal',
    description: 'Instrument / data connection between a device and its control.',
    dash: '6 4',
    width: 1.5,
  },
  electrical: {
    label: 'Electrical',
    description: 'Electrical power or wiring.',
    dash: '2 3',
    width: 1.5,
  },
  pneumatic: {
    label: 'Pneumatic',
    description: 'Pneumatic (air) signal line.',
    dash: '8 3 2 3',
    width: 1.5,
  },
};

export const DEFAULT_LINE_TYPE: LineType = 'process';

export function lineStyle(lineType: LineType | undefined): LineStyle {
  return LINE_STYLES[lineType ?? DEFAULT_LINE_TYPE];
}
