/**
 * 🧠 CLAWCORE NEURON ROUTER (v1.0)
 * El punto de inyección de nuevas capacidades.
 */

export interface Neuron {
  id: string;
  type: 'vision' | 'audit' | 'market' | 'logic';
  execute: (payload: any) => Promise<any>;
}

export class NeuronRouter {
  private neurons: Map<string, Neuron> = new Map();

  /**
   * Inyecta una nueva neurona sin modificar el Core.
   */
  register(neuron: Neuron) {
    console.log(`🧠 [NeuronRouter]: Registrando capacidad: ${neuron.id}`);
    this.neurons.set(neuron.id, neuron);
  }

  /**
   * Canaliza la tarea a la neurona especializada.
   */
  async route(neuronId: string, payload: any) {
    const neuron = this.neurons.get(neuronId);
    return neuron ? await neuron.execute(payload) : null;
  }
}
