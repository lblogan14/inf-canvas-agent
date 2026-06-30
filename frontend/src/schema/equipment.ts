/**
 * Equipment taxonomy for P&ID canvases.
 *
 * `EquipmentType` is the stable key used everywhere (frontend symbols, backend
 * agents, persisted JSON). `EQUIPMENT_METADATA` carries the rendering + port
 * information that both the Vue symbol components and the AI agents rely on, so
 * there is exactly one place that defines "what a pump is".
 */

export const EQUIPMENT_TYPES = [
  'centrifugal_pump',
  'positive_displacement_pump',
  'gate_valve',
  'globe_valve',
  'control_valve',
  'check_valve',
  'ball_valve',
  'vessel',
  'column',
  'storage_tank',
  'shell_tube_heat_exchanger',
  'compressor',
  'instrument',
] as const;

export type EquipmentType = (typeof EQUIPMENT_TYPES)[number];

/** Symbol component families (maps to files in canvas/nodes/symbols). */
export type SymbolKey =
  'pump' | 'valve' | 'vessel' | 'tank' | 'heat_exchanger' | 'compressor' | 'instrument';

export type PortRole = 'inlet' | 'outlet' | 'inout';
export type PortSide = 'top' | 'right' | 'bottom' | 'left';

export interface PortDef {
  /** Stable id, unique within a node (e.g. "in", "out", "suction"). */
  id: string;
  role: PortRole;
  side: PortSide;
  label?: string;
}

export type EquipmentCategory =
  'pump' | 'valve' | 'vessel' | 'exchanger' | 'compressor' | 'instrument';

export interface EquipmentMeta {
  type: EquipmentType;
  /** Human-readable name shown in the UI and used in prompts. */
  label: string;
  category: EquipmentCategory;
  /** Which SVG symbol component renders this type. */
  symbol: SymbolKey;
  /** Default node footprint in canvas units. */
  size: { width: number; height: number };
  ports: PortDef[];
}

const IN_OUT: PortDef[] = [
  { id: 'in', role: 'inlet', side: 'left' },
  { id: 'out', role: 'outlet', side: 'right' },
];

export const EQUIPMENT_METADATA: Record<EquipmentType, EquipmentMeta> = {
  centrifugal_pump: {
    type: 'centrifugal_pump',
    label: 'Centrifugal Pump',
    category: 'pump',
    symbol: 'pump',
    size: { width: 80, height: 80 },
    ports: [
      { id: 'suction', role: 'inlet', side: 'left' },
      { id: 'discharge', role: 'outlet', side: 'top' },
    ],
  },
  positive_displacement_pump: {
    type: 'positive_displacement_pump',
    label: 'Positive Displacement Pump',
    category: 'pump',
    symbol: 'pump',
    size: { width: 80, height: 80 },
    ports: [
      { id: 'suction', role: 'inlet', side: 'left' },
      { id: 'discharge', role: 'outlet', side: 'right' },
    ],
  },
  gate_valve: {
    type: 'gate_valve',
    label: 'Gate Valve',
    category: 'valve',
    symbol: 'valve',
    size: { width: 60, height: 40 },
    ports: IN_OUT,
  },
  globe_valve: {
    type: 'globe_valve',
    label: 'Globe Valve',
    category: 'valve',
    symbol: 'valve',
    size: { width: 60, height: 40 },
    ports: IN_OUT,
  },
  control_valve: {
    type: 'control_valve',
    label: 'Control Valve',
    category: 'valve',
    symbol: 'valve',
    size: { width: 60, height: 56 },
    ports: IN_OUT,
  },
  check_valve: {
    type: 'check_valve',
    label: 'Check Valve',
    category: 'valve',
    symbol: 'valve',
    size: { width: 60, height: 40 },
    ports: IN_OUT,
  },
  ball_valve: {
    type: 'ball_valve',
    label: 'Ball Valve',
    category: 'valve',
    symbol: 'valve',
    size: { width: 60, height: 40 },
    ports: IN_OUT,
  },
  vessel: {
    type: 'vessel',
    label: 'Vessel / Drum',
    category: 'vessel',
    symbol: 'vessel',
    size: { width: 100, height: 140 },
    ports: [
      { id: 'top', role: 'inout', side: 'top' },
      { id: 'bottom', role: 'outlet', side: 'bottom' },
      { id: 'side_in', role: 'inlet', side: 'left' },
      { id: 'side_out', role: 'outlet', side: 'right' },
    ],
  },
  column: {
    type: 'column',
    label: 'Column / Tower',
    category: 'vessel',
    symbol: 'vessel',
    size: { width: 90, height: 200 },
    ports: [
      { id: 'overhead', role: 'outlet', side: 'top' },
      { id: 'bottoms', role: 'outlet', side: 'bottom' },
      { id: 'feed', role: 'inlet', side: 'left' },
    ],
  },
  storage_tank: {
    type: 'storage_tank',
    label: 'Storage Tank',
    category: 'vessel',
    symbol: 'tank',
    size: { width: 140, height: 120 },
    ports: [
      { id: 'fill', role: 'inlet', side: 'top' },
      { id: 'draw', role: 'outlet', side: 'bottom' },
    ],
  },
  shell_tube_heat_exchanger: {
    type: 'shell_tube_heat_exchanger',
    label: 'Shell & Tube Heat Exchanger',
    category: 'exchanger',
    symbol: 'heat_exchanger',
    size: { width: 120, height: 80 },
    ports: [
      { id: 'shell_in', role: 'inlet', side: 'left' },
      { id: 'shell_out', role: 'outlet', side: 'right' },
      { id: 'tube_in', role: 'inlet', side: 'top' },
      { id: 'tube_out', role: 'outlet', side: 'bottom' },
    ],
  },
  compressor: {
    type: 'compressor',
    label: 'Compressor',
    category: 'compressor',
    symbol: 'compressor',
    size: { width: 90, height: 80 },
    ports: [
      { id: 'suction', role: 'inlet', side: 'left' },
      { id: 'discharge', role: 'outlet', side: 'right' },
    ],
  },
  instrument: {
    type: 'instrument',
    label: 'Instrument',
    category: 'instrument',
    symbol: 'instrument',
    size: { width: 56, height: 56 },
    ports: [{ id: 'signal', role: 'inout', side: 'bottom' }],
  },
};

export function isEquipmentType(value: string): value is EquipmentType {
  return (EQUIPMENT_TYPES as readonly string[]).includes(value);
}

export function getEquipmentMeta(type: EquipmentType): EquipmentMeta {
  return EQUIPMENT_METADATA[type];
}
