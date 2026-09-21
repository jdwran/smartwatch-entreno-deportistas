import {
  AthleteProfile,
  WorkoutSession,
  SleepRecord,
  DailyReadiness,
  HRVReading,
  WorkloadDay,
  ProviderConnection,
  FatigueAnalysis,
  OrthostaticTestRecord
} from '../types';

const API_BASE = 'http://localhost:8000/api';

export async function getAthletes(): Promise<AthleteProfile[]> {
  const res = await fetch(`${API_BASE}/athletes`);
  if (!res.ok) throw new Error('Error al cargar atletas');
  return res.json();
}

export async function getReadiness(athleteId: string): Promise<{
  current: DailyReadiness;
  history: DailyReadiness[];
  hrv_readings: HRVReading[];
}> {
  const res = await fetch(`${API_BASE}/athletes/${athleteId}/readiness`);
  if (!res.ok) throw new Error('Error al cargar métricas de preparación');
  return res.json();
}

export async function getWorkouts(athleteId: string): Promise<WorkoutSession[]> {
  const res = await fetch(`${API_BASE}/athletes/${athleteId}/workouts`);
  if (!res.ok) throw new Error('Error al cargar entrenamientos');
  return res.json();
}

export async function getSleep(athleteId: string): Promise<{
  current: SleepRecord | null;
  history: SleepRecord[];
  averages: {
    efficiency: number;
    deep_minutes: number;
    rem_minutes: number;
    score: number;
  };
}> {
  const res = await fetch(`${API_BASE}/athletes/${athleteId}/sleep`);
  if (!res.ok) throw new Error('Error al cargar datos de sueño');
  return res.json();
}

export async function getWorkload(athleteId: string): Promise<{
  current: WorkloadDay | null;
  history: WorkloadDay[];
}> {
  const res = await fetch(`${API_BASE}/athletes/${athleteId}/workload`);
  if (!res.ok) throw new Error('Error al cargar carga de entrenamiento');
  return res.json();
}

export async function getIntegrations(athleteId: string): Promise<ProviderConnection[]> {
  const res = await fetch(`${API_BASE}/athletes/${athleteId}/integrations`);
  if (!res.ok) throw new Error('Error al cargar conexiones de dispositivos');
  return res.json();
}

export async function toggleIntegration(athleteId: string, providerId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/athletes/${athleteId}/integrations/${providerId}/toggle`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Error al alternar conexión');
  return res.json();
}

export async function uploadFitFile(athleteId: string, file: File): Promise<{
  status: string;
  message: string;
  workout: WorkoutSession;
}> {
  const formData = new FormData();
  formData.append('athlete_id', athleteId);
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/upload/fit`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('Error al procesar archivo .FIT');
  return res.json();
}

export async function getFatigue(athleteId: string): Promise<{
  current: FatigueAnalysis;
  history: FatigueAnalysis[];
  latest_orthostatic: OrthostaticTestRecord | null;
}> {
  const res = await fetch(`${API_BASE}/athletes/${athleteId}/fatigue`);
  if (!res.ok) throw new Error('Error al cargar nivel de fatiga');
  return res.json();
}

export async function getOrthostaticTests(athleteId: string): Promise<OrthostaticTestRecord[]> {
  const res = await fetch(`${API_BASE}/athletes/${athleteId}/orthostatic-tests`);
  if (!res.ok) throw new Error('Error al cargar tests ortostáticos');
  return res.json();
}

export async function runOrthostaticTest(athleteId: string, deviceName = 'Polar H10 (Banda ECG)'): Promise<OrthostaticTestRecord> {
  const res = await fetch(`${API_BASE}/athletes/${athleteId}/orthostatic-test?device_name=${encodeURIComponent(deviceName)}`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Error al ejecutar test ortostático');
  return res.json();
}

