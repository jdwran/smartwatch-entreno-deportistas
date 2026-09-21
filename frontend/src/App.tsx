import React, { useState, useEffect } from 'react';
import {
  AthleteProfile,
  DailyReadiness,
  WorkoutSession,
  SleepRecord,
  WorkloadDay,
  HRVReading,
  ProviderConnection,
  FatigueAnalysis,
  OrthostaticTestRecord
} from './types';
import {
  getAthletes,
  getReadiness,
  getWorkouts,
  getSleep,
  getWorkload,
  getIntegrations,
  getFatigue
} from './services/api';
import { Header } from './components/Header';
import { ReadinessCard } from './components/ReadinessCard';
import { HRVDeepDive } from './components/HRVDeepDive';
import { WorkloadEnergyView } from './components/WorkloadEnergyView';
import { SleepArchitectureView } from './components/SleepArchitectureView';
import { FatigueAnalysisView } from './components/FatigueAnalysisView';
import { DeviceIntegrationsModal } from './components/DeviceIntegrationsModal';
import {
  Activity,
  Heart,
  Flame,
  Moon,
  Watch,
  TrendingUp,
  Sliders,
  AlertCircle,
  ShieldAlert
} from 'lucide-react';

export function App() {
  const [athletes, setAthletes] = useState<AthleteProfile[]>([]);
  const [selectedAthlete, setSelectedAthlete] = useState<AthleteProfile | null>(null);
  
  const [readinessData, setReadinessData] = useState<{
    current: DailyReadiness | null;
    history: DailyReadiness[];
    hrv_readings: HRVReading[];
  }>({ current: null, history: [], hrv_readings: [] });

  const [workouts, setWorkouts] = useState<WorkoutSession[]>([]);
  
  const [sleepData, setSleepData] = useState<{
    current: SleepRecord | null;
    history: SleepRecord[];
    averages: {
      efficiency: number;
      deep_minutes: number;
      rem_minutes: number;
      score: number;
    };
  } | null>(null);

  const [workloadData, setWorkloadData] = useState<{
    current: WorkloadDay | null;
    history: WorkloadDay[];
  }>({ current: null, history: [] });

  const [connections, setConnections] = useState<ProviderConnection[]>([]);

  const [fatigueData, setFatigueData] = useState<{
    current: FatigueAnalysis | null;
    history: FatigueAnalysis[];
    latest_orthostatic: OrthostaticTestRecord | null;
  }>({ current: null, history: [], latest_orthostatic: null });
  
  const [activeTab, setActiveTab] = useState<'readiness' | 'fatigue' | 'workload' | 'sleep' | 'hrv'>('readiness');
  const [isDevicesModalOpen, setIsDevicesModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initial load
  useEffect(() => {
    async function init() {
      try {
        setLoading(true);
        const athleteList = await getAthletes();
        setAthletes(athleteList);
        if (athleteList.length > 0) {
          setSelectedAthlete(athleteList[0]);
        }
      } catch (err: any) {
        setError(err.message || 'Error al conectar con el backend de telemetría.');
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  // Fetch athlete specific data
  const loadAthleteData = async (athleteId: string) => {
    try {
      setLoading(true);
      setError(null);
      const [readinessRes, workoutsRes, sleepRes, workloadRes, connsRes, fatigueRes] = await Promise.all([
        getReadiness(athleteId),
        getWorkouts(athleteId),
        getSleep(athleteId),
        getWorkload(athleteId),
        getIntegrations(athleteId),
        getFatigue(athleteId)
      ]);

      setReadinessData(readinessRes);
      setWorkouts(workoutsRes);
      setSleepData(sleepRes);
      setWorkloadData(workloadRes);
      setConnections(connsRes);
      setFatigueData(fatigueRes);
    } catch (err: any) {
      setError(err.message || 'Error al actualizar métricas del atleta.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedAthlete) {
      loadAthleteData(selectedAthlete.id);
    }
  }, [selectedAthlete]);

  const handleRefresh = () => {
    if (selectedAthlete) {
      loadAthleteData(selectedAthlete.id);
    }
  };

  return (
    <div className="min-h-screen bg-[#080b11] text-slate-100 flex flex-col">
      
      {/* Top Navbar */}
      <Header
        athletes={athletes}
        selectedAthlete={selectedAthlete}
        onSelectAthlete={setSelectedAthlete}
        connections={connections}
        onOpenDevices={() => setIsDevicesModalOpen(true)}
        onRefresh={handleRefresh}
        loading={loading}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-6 space-y-6">
        
        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-3">
            <AlertCircle className="h-5 w-5 flex-shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {/* Athlete Overview & Readiness Card */}
        {selectedAthlete && readinessData.current && (
          <ReadinessCard
            athlete={selectedAthlete}
            readiness={readinessData.current}
            hrvLatest={readinessData.hrv_readings[readinessData.hrv_readings.length - 1]}
          />
        )}

        {/* Tab Navigation */}
        <div className="flex flex-wrap items-center justify-between border-b border-slate-800/80 pb-2 gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={() => setActiveTab('readiness')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer ${
                activeTab === 'readiness'
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-900/60'
              }`}
            >
              <Activity className="h-4 w-4" />
              Preparación General
            </button>

            <button
              onClick={() => setActiveTab('fatigue')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer ${
                activeTab === 'fatigue'
                  ? 'bg-amber-500/15 text-amber-300 border border-amber-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-900/60'
              }`}
            >
              <ShieldAlert className="h-4 w-4 text-amber-400" />
              Nivel de Fatiga & Sensores
              {fatigueData.current && (
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-black border ${
                  fatigueData.current.overall_fatigue_score > 60
                    ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                    : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                }`}>
                  {fatigueData.current.overall_fatigue_score}/100
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('hrv')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer ${
                activeTab === 'hrv'
                  ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-900/60'
              }`}
            >
              <Heart className="h-4 w-4" />
              Variabilidad Cardíaca (HRV)
            </button>

            <button
              onClick={() => setActiveTab('workload')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer ${
                activeTab === 'workload'
                  ? 'bg-orange-500/10 text-orange-400 border border-orange-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-900/60'
              }`}
            >
              <Flame className="h-4 w-4" />
              Gasto Energético & Carga (ACWR)
            </button>

            <button
              onClick={() => setActiveTab('sleep')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer ${
                activeTab === 'sleep'
                  ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-900/60'
              }`}
            >
              <Moon className="h-4 w-4" />
              Arquitectura del Sueño
            </button>
          </div>

          <button
            onClick={() => setIsDevicesModalOpen(true)}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-700 hover:border-cyan-400/50 text-xs font-semibold text-slate-200 transition cursor-pointer"
          >
            <Watch className="h-4 w-4 text-cyan-400" />
            Vincular Sensores / Subir .FIT
          </button>
        </div>

        {/* Tab Views */}
        {activeTab === 'readiness' && selectedAthlete && (
          <div className="space-y-6">
            <FatigueAnalysisView
              fatigueData={fatigueData}
              athleteId={selectedAthlete.id}
              onRefresh={() => loadAthleteData(selectedAthlete.id)}
            />
            <HRVDeepDive
              hrvReadings={readinessData.hrv_readings}
              currentReadiness={readinessData.current}
            />
            <WorkloadEnergyView
              workouts={workouts}
              workloadHistory={workloadData.history}
            />
          </div>
        )}

        {activeTab === 'fatigue' && selectedAthlete && (
          <FatigueAnalysisView
            fatigueData={fatigueData}
            athleteId={selectedAthlete.id}
            onRefresh={() => loadAthleteData(selectedAthlete.id)}
          />
        )}

        {activeTab === 'hrv' && (
          <HRVDeepDive
            hrvReadings={readinessData.hrv_readings}
            currentReadiness={readinessData.current}
          />
        )}

        {activeTab === 'workload' && (
          <WorkloadEnergyView
            workouts={workouts}
            workloadHistory={workloadData.history}
          />
        )}

        {activeTab === 'sleep' && (
          <SleepArchitectureView
            sleepData={sleepData}
          />
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#090d16] py-4 px-4 text-center text-xs text-slate-500">
        <p>
          APEX PRO TELEMETRY © 2026 — Plataforma Universal de Alto Rendimiento para Smartwatches (Garmin, Polar, Whoop, Apple Watch).
        </p>
      </footer>

      {/* Device & FIT Upload Modal */}
      {selectedAthlete && (
        <DeviceIntegrationsModal
          isOpen={isDevicesModalOpen}
          onClose={() => setIsDevicesModalOpen(false)}
          connections={connections}
          athleteId={selectedAthlete.id}
          onRefreshData={() => loadAthleteData(selectedAthlete.id)}
        />
      )}

    </div>
  );
}

export default App;
