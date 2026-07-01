/**
 * Equipment taxonomy for P&ID canvases.
 *
 * `EquipmentType` is the stable key used everywhere. `EQUIPMENT_METADATA` carries
 * rendering + port info shared by the Vue symbol layer and the AI agents, so
 * there is one place that defines "what a pump is". Symbols are ISA/ISO-styled
 * SVGs under `src/assets/symbols/`, keyed by `SymbolKey`.
 */

export const EQUIPMENT_TYPES = [
  // pumps
  'centrifugal_pump',
  'positive_displacement_pump',
  // compressors / blowers
  'compressor',
  'blower',
  'fan',
  // drivers
  'motor',
  'turbine',
  // valves
  'gate_valve',
  'globe_valve',
  'ball_valve',
  'butterfly_valve',
  'check_valve',
  'control_valve',
  'three_way_valve',
  'relief_valve',
  // vessels
  'vessel',
  'column',
  'reactor',
  'mixer',
  // tanks
  'storage_tank',
  // exchangers
  'shell_tube_heat_exchanger',
  'air_cooler',
  'cooling_tower',
  // separation
  'filter',
  // instrument
  'instrument',
] as const;

export type EquipmentType = (typeof EQUIPMENT_TYPES)[number];

/** SVG symbol keys (one per file in assets/symbols). */
export type SymbolKey =
  | 'pump_centrifugal'
  | 'pump_pd'
  | 'compressor'
  | 'blower'
  | 'motor'
  | 'turbine'
  | 'valve_gate'
  | 'valve_globe'
  | 'valve_ball'
  | 'valve_butterfly'
  | 'valve_check'
  | 'valve_control'
  | 'valve_threeway'
  | 'valve_relief'
  | 'vessel'
  | 'column'
  | 'reactor'
  | 'mixer'
  | 'tank'
  | 'heat_exchanger'
  | 'air_cooler'
  | 'cooling_tower'
  | 'filter'
  | 'instrument';

export type PortRole = 'inlet' | 'outlet' | 'inout';
export type PortSide = 'top' | 'right' | 'bottom' | 'left';

export interface PortDef {
  id: string;
  role: PortRole;
  side: PortSide;
  label?: string;
}

export type EquipmentCategory =
  | 'pump'
  | 'compressor'
  | 'driver'
  | 'valve'
  | 'vessel'
  | 'tank'
  | 'exchanger'
  | 'separation'
  | 'instrument';

export interface EquipmentMeta {
  type: EquipmentType;
  label: string;
  category: EquipmentCategory;
  symbol: SymbolKey;
  size: { width: number; height: number };
  ports: PortDef[];
}

const IN_OUT: PortDef[] = [
  { id: 'in', role: 'inlet', side: 'left' },
  { id: 'out', role: 'outlet', side: 'right' },
];

function meta(
  type: EquipmentType,
  label: string,
  category: EquipmentCategory,
  symbol: SymbolKey,
  width: number,
  height: number,
  ports: PortDef[],
): EquipmentMeta {
  return { type, label, category, symbol, size: { width, height }, ports };
}

export const EQUIPMENT_METADATA: Record<EquipmentType, EquipmentMeta> = {
  centrifugal_pump: meta(
    'centrifugal_pump',
    'Centrifugal Pump',
    'pump',
    'pump_centrifugal',
    80,
    80,
    [
      { id: 'suction', role: 'inlet', side: 'left' },
      { id: 'discharge', role: 'outlet', side: 'top' },
    ],
  ),
  positive_displacement_pump: meta(
    'positive_displacement_pump',
    'Positive Displacement Pump',
    'pump',
    'pump_pd',
    80,
    80,
    [
      { id: 'suction', role: 'inlet', side: 'left' },
      { id: 'discharge', role: 'outlet', side: 'right' },
    ],
  ),
  compressor: meta('compressor', 'Compressor', 'compressor', 'compressor', 92, 80, [
    { id: 'suction', role: 'inlet', side: 'left' },
    { id: 'discharge', role: 'outlet', side: 'right' },
  ]),
  blower: meta('blower', 'Blower', 'compressor', 'blower', 82, 80, IN_OUT),
  fan: meta('fan', 'Fan', 'compressor', 'blower', 80, 80, IN_OUT),
  motor: meta('motor', 'Motor', 'driver', 'motor', 70, 70, [
    { id: 'shaft', role: 'inout', side: 'right' },
  ]),
  turbine: meta('turbine', 'Turbine / Expander', 'driver', 'turbine', 92, 72, IN_OUT),
  gate_valve: meta('gate_valve', 'Gate Valve', 'valve', 'valve_gate', 64, 40, IN_OUT),
  globe_valve: meta('globe_valve', 'Globe Valve', 'valve', 'valve_globe', 64, 40, IN_OUT),
  ball_valve: meta('ball_valve', 'Ball Valve', 'valve', 'valve_ball', 64, 40, IN_OUT),
  butterfly_valve: meta(
    'butterfly_valve',
    'Butterfly Valve',
    'valve',
    'valve_butterfly',
    64,
    40,
    IN_OUT,
  ),
  check_valve: meta('check_valve', 'Check Valve', 'valve', 'valve_check', 64, 40, IN_OUT),
  control_valve: meta('control_valve', 'Control Valve', 'valve', 'valve_control', 64, 58, IN_OUT),
  three_way_valve: meta('three_way_valve', 'Three-Way Valve', 'valve', 'valve_threeway', 56, 56, [
    { id: 'in', role: 'inlet', side: 'left' },
    { id: 'out', role: 'outlet', side: 'right' },
    { id: 'branch', role: 'outlet', side: 'bottom' },
  ]),
  relief_valve: meta('relief_valve', 'Relief Valve', 'valve', 'valve_relief', 54, 66, [
    { id: 'in', role: 'inlet', side: 'bottom' },
    { id: 'out', role: 'outlet', side: 'left' },
  ]),
  vessel: meta('vessel', 'Vessel / Drum', 'vessel', 'vessel', 100, 140, [
    { id: 'top', role: 'inout', side: 'top' },
    { id: 'bottom', role: 'outlet', side: 'bottom' },
    { id: 'side_in', role: 'inlet', side: 'left' },
    { id: 'side_out', role: 'outlet', side: 'right' },
  ]),
  column: meta('column', 'Column / Tower', 'vessel', 'column', 92, 200, [
    { id: 'overhead', role: 'outlet', side: 'top' },
    { id: 'bottoms', role: 'outlet', side: 'bottom' },
    { id: 'feed', role: 'inlet', side: 'left' },
  ]),
  reactor: meta('reactor', 'Reactor', 'vessel', 'reactor', 110, 150, [
    { id: 'feed', role: 'inlet', side: 'top' },
    { id: 'product', role: 'outlet', side: 'bottom' },
    { id: 'jacket_in', role: 'inlet', side: 'left' },
    { id: 'jacket_out', role: 'outlet', side: 'right' },
  ]),
  mixer: meta('mixer', 'Mixer / Agitated Tank', 'vessel', 'mixer', 112, 120, [
    { id: 'in', role: 'inlet', side: 'left' },
    { id: 'out', role: 'outlet', side: 'bottom' },
  ]),
  storage_tank: meta('storage_tank', 'Storage Tank', 'tank', 'tank', 140, 116, [
    { id: 'fill', role: 'inlet', side: 'top' },
    { id: 'draw', role: 'outlet', side: 'bottom' },
  ]),
  shell_tube_heat_exchanger: meta(
    'shell_tube_heat_exchanger',
    'Shell & Tube Heat Exchanger',
    'exchanger',
    'heat_exchanger',
    120,
    80,
    [
      { id: 'shell_in', role: 'inlet', side: 'left' },
      { id: 'shell_out', role: 'outlet', side: 'right' },
      { id: 'tube_in', role: 'inlet', side: 'top' },
      { id: 'tube_out', role: 'outlet', side: 'bottom' },
    ],
  ),
  air_cooler: meta('air_cooler', 'Air Cooler', 'exchanger', 'air_cooler', 120, 84, IN_OUT),
  cooling_tower: meta('cooling_tower', 'Cooling Tower', 'exchanger', 'cooling_tower', 120, 110, [
    { id: 'in', role: 'inlet', side: 'top' },
    { id: 'out', role: 'outlet', side: 'bottom' },
  ]),
  filter: meta('filter', 'Filter', 'separation', 'filter', 72, 96, [
    { id: 'in', role: 'inlet', side: 'top' },
    { id: 'out', role: 'outlet', side: 'bottom' },
  ]),
  instrument: meta('instrument', 'Instrument', 'instrument', 'instrument', 56, 56, [
    { id: 'signal', role: 'inout', side: 'bottom' },
  ]),
};

export function isEquipmentType(value: string): value is EquipmentType {
  return (EQUIPMENT_TYPES as readonly string[]).includes(value);
}

export function getEquipmentMeta(type: EquipmentType): EquipmentMeta {
  return EQUIPMENT_METADATA[type];
}
