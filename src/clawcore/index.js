// 🚀 CLAWCORE - SISTEMA EVOLUTIVO COMPLETO
// Versión: 2026.2.16-clawcore
// Integración completa de todos los componentes

const ClawCoreDoctor = require('./doctor');
const ContinuityProtocol = require('./continuity');
const HybridMeshArchitecture = require('./architecture');

class ClawCoreSystem {
  constructor() {
    this.doctor = new ClawCoreDoctor();
    this.continuity = new ContinuityProtocol();
    this.architecture = new HybridMeshArchitecture();
    this.identity = this.getIdentity();
    this.errors = [];
    this.solutions = [];
  }

  getIdentity() {
    return {
      name: 'ClawCore Evolutivo',
      version: '2026.2.16-clawcore',
      base: 'ClawCore 2026.2.9',
      improvements: [
        'Fix bug TUI (model display)',
        'Hybrid Mesh Architecture',
        '14 bilingual neurons',
        'Auto-repair system',
        'Continuity Protocol',
        'ChromaDB integration',
        'Autonomy growth system'
      ],
      location: 'VPS229 (15.204.231.229)',
      resources: '24GB RAM, 8 CPUs, 168GB free',
      model: 'Llama 3.2 3B via Ollama',
      gateway: 'ws://127.0.0.1:18789'
    };
  }

  diagnose() {
    const doctorReport = this.doctor.diagnose();
    const architecture = this.architecture.getArchitecture();
    const context = this.continuity.getContext();
    
    return {
      timestamp: new Date().toISOString(),
      system: 'ClawCore Complete Integration',
      status: 'OPERATIONAL',
      components: {
        doctor: doctorReport,
        architecture: architecture,
        continuity: context,
        errors: this.errors.length,
        solutions: this.solutions.length
      },
      recommendations: this.getRecommendations()
    };
  }

  getRecommendations() {
    return [
      'Complete ChromaDB reinstallation',
      'Neuron optimization for <3ms response',
      'Increase autonomy to 50%',
      'Implement full error solution database',
      'Integrate all 14 neurons into TUI'
    ];
  }

  logError(error, solution) {
    this.errors.push({
      error,
      timestamp: new Date().toISOString(),
      solved: !!solution
    });
    
    if (solution) {
      this.solutions.push({
        error,
        solution,
        timestamp: new Date().toISOString(),
        applied: true
      });
      return this.doctor.autoRepair(error);
    }
    
    return null;
  }

  getErrorSolutions() {
    return {
      totalErrors: this.errors.length,
      solved: this.solutions.length,
      unsolved: this.errors.length - this.solutions.length,
      solutions: this.solutions.slice(-10),
      commonErrors: this.getCommonErrors()
    };
  }

  getCommonErrors() {
    const errors = [
      'TUI shows unknown for model',
      'Qwen 7B identifies as Claude',
      'Configuration conflicts',
      'Multiple defaultModel settings',
      'Cache persistence issues'
    ];
    
    return errors.map(error => ({
      error,
      solution: this.getSolutionForError(error),
      implemented: true
    }));
  }

  getSolutionForError(error) {
    const solutions = {
      'TUI shows unknown for model': 'Fixed in tui-status-summary.ts line 67',
      'Qwen 7B identifies as Claude': 'Switched to Llama 3.2 3B',
      'Configuration conflicts': 'Cleaned models.json, only Ollama provider',
      'Multiple defaultModel settings': 'Removed defaultModel from providers',
      'Cache persistence issues': 'Radical cleanup: rm -rf ~/.clawcore/cache'
    };
    
    return solutions[error] || 'Solution in development';
  }
}

module.exports = ClawCoreSystem;
