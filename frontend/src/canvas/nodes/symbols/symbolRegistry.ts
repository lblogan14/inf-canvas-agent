import type { Component } from 'vue';
import type { SymbolKey } from '@/schema';
import PumpSymbol from './PumpSymbol.vue';
import ValveSymbol from './ValveSymbol.vue';
import VesselSymbol from './VesselSymbol.vue';
import TankSymbol from './TankSymbol.vue';
import HeatExchangerSymbol from './HeatExchangerSymbol.vue';
import CompressorSymbol from './CompressorSymbol.vue';
import InstrumentSymbol from './InstrumentSymbol.vue';

export const symbolRegistry: Record<SymbolKey, Component> = {
  pump: PumpSymbol,
  valve: ValveSymbol,
  vessel: VesselSymbol,
  tank: TankSymbol,
  heat_exchanger: HeatExchangerSymbol,
  compressor: CompressorSymbol,
  instrument: InstrumentSymbol,
};
