export interface HeartRateZone {
  zone: number;
  name: string;
  min_hr: number;
  max_hr: number;
  time_in_seconds: number;
  percentage: number;
}

export interface AthleteProfile {
  id: string;
  name: string;
  sport: string;
  age: number;
  gender: string;
  weight_kg: number;
  height_cm: number;
  resting_hr: number;
  max_hr: number;
  vo2max: number;
}

export interface WorkoutSession {
  id: string;
  athlete_id: string;
  device_brand: string;
  device_model?: string;
  sport_type: string;
  start_time: string;
  end_time: string;
  duration_seconds: number;
  distance_meters?: number;
  avg_hr: number;
  max_hr: number;
  calories_burned: number;
  trimp_edwards: number;
  trimp_banister: number;
  zones: HeartRateZone[];
  hr_stream_sample?: number[];
  source: string;
}

export interface HRVReading {
  id: string;
  athlete_id: string;
  timestamp: string;
  rmssd: number;
  sdnn?: number;
  ln_rmssd: number;
  baseline_7d_mean: number;
  baseline_7d_sd: number;
  swc_lower: number;
  swc_upper: number;
  status: 'optimal' | 'sympathetic_fatigue' | 'parasympathetic_saturation' | 'under_recovered';
  source_device: string;
}

export interface SleepStage {
  stage: string;
  minutes: number;
  percentage: number;
}

export interface SleepRecord {
  id: string;
  athlete_id: string;
  date: string;
  start_time: string;
  end_time: string;
  total_sleep_minutes: number;
  time_in_bed_minutes: number;
  efficiency_percentage: number;
  deep_sleep_minutes: number;
  rem_sleep_minutes: number;
  light_sleep_minutes: number;
  awake_minutes: number;
  stages: SleepStage[];
  nocturnal_rhr: number;
  nocturnal_hrv_rmssd: number;
  daytime_rhr_baseline: number;
  hr_dip_percentage: number;
  sleep_score: number;
  source_device: string;
}

export interface WorkloadDay {
  date: string;
  daily_trimp: number;
  acute_load: number;
  chronic_load: number;
  acwr: number;
  zone_category: string;
}

export interface DailyReadiness {
  date: string;
  athlete_id: string;
  readiness_score: number;
  hrv_rmssd: number;
  hrv_ln_rmssd: number;
  hrv_status: string;
  sleep_score: number;
  acute_load: number;
  chronic_load: number;
  acwr: number;
  training_recommendation: string;
  intensity_target: string;
}

export interface ProviderConnection {
  provider_id: string;
  name: string;
  connected: boolean;
  last_sync?: string;
  account_email?: string;
  supported_metrics: string[];
  auth_type: string;
}
