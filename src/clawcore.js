import MarketNeuron from './market.js';

export default class ClawCoreSystem {
    constructor() {
        this.market = new MarketNeuron();
    }
    async start() {
        console.log('🧠 [Cerebro]: Cargando protocolos de soberanía...');
        console.log('📡 [Red]: Conectando a nodos maestros...');
        await this.market.analyze();
        return true;
    }
}
