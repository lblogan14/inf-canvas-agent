import type { SymbolKey } from '@/schema';

// ISA/ISO-styled symbols authored as SVG files and imported as raw markup so
// they can be inlined (keeps `currentColor` theming + selection highlight).
import pump_centrifugal from '@/assets/symbols/pump_centrifugal.svg?raw';
import pump_pd from '@/assets/symbols/pump_pd.svg?raw';
import compressor from '@/assets/symbols/compressor.svg?raw';
import blower from '@/assets/symbols/blower.svg?raw';
import motor from '@/assets/symbols/motor.svg?raw';
import turbine from '@/assets/symbols/turbine.svg?raw';
import valve_gate from '@/assets/symbols/valve_gate.svg?raw';
import valve_globe from '@/assets/symbols/valve_globe.svg?raw';
import valve_ball from '@/assets/symbols/valve_ball.svg?raw';
import valve_butterfly from '@/assets/symbols/valve_butterfly.svg?raw';
import valve_check from '@/assets/symbols/valve_check.svg?raw';
import valve_control from '@/assets/symbols/valve_control.svg?raw';
import valve_threeway from '@/assets/symbols/valve_threeway.svg?raw';
import valve_relief from '@/assets/symbols/valve_relief.svg?raw';
import vessel from '@/assets/symbols/vessel.svg?raw';
import column from '@/assets/symbols/column.svg?raw';
import reactor from '@/assets/symbols/reactor.svg?raw';
import mixer from '@/assets/symbols/mixer.svg?raw';
import tank from '@/assets/symbols/tank.svg?raw';
import heat_exchanger from '@/assets/symbols/heat_exchanger.svg?raw';
import air_cooler from '@/assets/symbols/air_cooler.svg?raw';
import cooling_tower from '@/assets/symbols/cooling_tower.svg?raw';
import filter from '@/assets/symbols/filter.svg?raw';
import instrument from '@/assets/symbols/instrument.svg?raw';

export const symbolRegistry: Record<SymbolKey, string> = {
  pump_centrifugal,
  pump_pd,
  compressor,
  blower,
  motor,
  turbine,
  valve_gate,
  valve_globe,
  valve_ball,
  valve_butterfly,
  valve_check,
  valve_control,
  valve_threeway,
  valve_relief,
  vessel,
  column,
  reactor,
  mixer,
  tank,
  heat_exchanger,
  air_cooler,
  cooling_tower,
  filter,
  instrument,
};
