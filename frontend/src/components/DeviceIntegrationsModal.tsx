import React, { useState, useRef } from 'react';
import { ProviderConnection, WorkoutSession } from '../types';
import { Watch, CheckCircle, XCircle, UploadCloud, RefreshCw, X, Shield, FileText, Check } from 'lucide-react';
import { toggleIntegration, uploadFitFile } from '../services/api';

interface DeviceIntegrationsModalProps {
  isOpen: boolean;
  onClose: () => void;
  connections: ProviderConnection[];
  athleteId: string;
  onRefreshData: () => void;
}

export const DeviceIntegrationsModal: React.FC<DeviceIntegrationsModalProps> = ({
  isOpen,
  onClose,
  connections,
  athleteId,
  onRefreshData
}) => {
  const [loadingProvider, setLoadingProvider] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [lastParsedWorkout, setLastParsedWorkout] = useState<WorkoutSession | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleToggle = async (providerId: string) => {
    setLoadingProvider(providerId);
    try {
      await toggleIntegration(athleteId, providerId);
      onRefreshData();
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingProvider(null);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    const file = files[0];
    
    setUploading(true);
    setUploadSuccess(null);
    setLastParsedWorkout(null);

    try {
      const res = await uploadFitFile(athleteId, file);
      setUploadSuccess(res.message);
      setLastParsedWorkout(res.workout);
      onRefreshData();
    } catch (err: any) {
      alert(err.message || 'Error al subir archivo .FIT');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-3xl rounded-2xl bg-[#0c1017] border border-slate-800 shadow-2xl max-h-[90vh] flex flex-col overflow-hidden">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-[#090d16]">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Watch className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Hub de Dispositivos e Integraciones</h3>
              <p className="text-xs text-slate-400">
                Conecta tus ecosistemas de reloj inteligente (Garmin, Polar, Whoop) o sube archivos .FIT
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          
          {/* Section 1: Cloud API Integrations */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
              <Shield className="h-4 w-4 text-cyan-400" />
              Conexiones Cloud OAuth2 & Webhooks
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {connections.map((conn) => (
                <div
                  key={conn.provider_id}
                  className={`p-4 rounded-xl border transition ${
                    conn.connected
                      ? 'bg-slate-900/80 border-cyan-500/30 shadow-sm'
                      : 'bg-slate-900/40 border-slate-800 opacity-80'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <h5 className="text-sm font-bold text-white flex items-center gap-2">
                        {conn.name}
                        {conn.connected ? (
                          <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                            <Check className="h-2.5 w-2.5" /> Sincronizado
                          </span>
                        ) : (
                          <span className="text-[10px] font-semibold text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">
                            Desconectado
                          </span>
                        )}
                      </h5>
                      <p className="text-[11px] text-slate-400">
                        {conn.account_email ? conn.account_email : 'Sin cuenta vinculada'}
                      </p>
                    </div>

                    <button
                      onClick={() => handleToggle(conn.provider_id)}
                      disabled={loadingProvider === conn.provider_id}
                      className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                        conn.connected
                          ? 'bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : 'bg-cyan-500 hover:bg-cyan-400 text-black font-bold shadow-md shadow-cyan-500/20'
                      }`}
                    >
                      {loadingProvider === conn.provider_id ? (
                        <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                      ) : conn.connected ? (
                        'Desconectar'
                      ) : (
                        'Conectar'
                      )}
                    </button>
                  </div>

                  <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-400 flex flex-wrap gap-1">
                    {conn.supported_metrics.map((m, idx) => (
                      <span key={idx} className="px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-300">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 2: Direct .FIT File Uploader */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-cyan-950/20 via-slate-900/60 to-slate-900/40 border border-cyan-500/20">
            <h4 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
              <UploadCloud className="h-5 w-5 text-cyan-400" />
              Importador Directo de Archivos .FIT / .TCX
            </h4>
            <p className="text-xs text-slate-400 mb-4">
              ¿No tienes claves API corporativas de Garmin o Polar? Arrastra directamente cualquier archivo <strong>.FIT</strong> extraído de tu reloj para procesar telemetría y calcular TRIMP y gasto energético de inmediato.
            </p>

            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-slate-700 hover:border-cyan-400/60 bg-slate-900/50 hover:bg-slate-900/80 rounded-xl p-6 text-center cursor-pointer transition flex flex-col items-center justify-center gap-2"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".fit,.tcx,.gpx"
                className="hidden"
                onChange={handleFileUpload}
              />
              <div className="h-12 w-12 rounded-full bg-cyan-500/10 flex items-center justify-center text-cyan-400">
                {uploading ? (
                  <RefreshCw className="h-6 w-6 animate-spin" />
                ) : (
                  <FileText className="h-6 w-6" />
                )}
              </div>
              <div className="text-sm font-semibold text-white">
                {uploading ? 'Decodificando archivo .FIT...' : 'Haz clic o arrastra aquí tu archivo .FIT o .TCX'}
              </div>
              <span className="text-[11px] text-slate-400">
                Compatible con Garmin Forerunner/Fenix/Edge, Polar Vantage/Grit, Wahoo BOLT, Coros Pace.
              </span>
            </div>

            {/* Upload feedback */}
            {uploadSuccess && (
              <div className="mt-4 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-2 text-xs text-emerald-300">
                <CheckCircle className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                <span>{uploadSuccess}</span>
              </div>
            )}

            {lastParsedWorkout && (
              <div className="mt-3 p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs space-y-1">
                <div className="font-bold text-white flex items-center justify-between">
                  <span>Sesión Decodificada: {lastParsedWorkout.sport_type}</span>
                  <span className="text-cyan-400">{lastParsedWorkout.device_brand}</span>
                </div>
                <div className="flex flex-wrap gap-3 text-slate-300 pt-1">
                  <span>Duración: {Math.round(lastParsedWorkout.duration_seconds / 60)} min</span>
                  <span>Gasto: <strong>{lastParsedWorkout.calories_burned} kcal</strong></span>
                  <span>TRIMP Edwards: <strong>{lastParsedWorkout.trimp_edwards}</strong></span>
                  <span>FC Media: <strong>{lastParsedWorkout.avg_hr} bpm</strong></span>
                </div>
              </div>
            )}
          </div>

        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-[#090d16] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition"
          >
            Cerrar
          </button>
        </div>

      </div>
    </div>
  );
};
