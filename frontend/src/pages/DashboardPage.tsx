import { useQuery } from '@tanstack/react-query';
import { projectsApi } from '@/services/projectsApi';
import { reportsApi } from '@/services/reportsApi';
import { BarChart3, FolderKanban, Wrench, AlertTriangle } from 'lucide-react';

export default function DashboardPage() {
  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.listProjects(),
  });

  const { data: semaforo } = useQuery({
    queryKey: ['semaforo-all'],
    queryFn: () => reportsApi.getSemaforo(),
  });

  const activeProjects = projects?.filter((p) => p.status === 'ACTIVO').length ?? 0;
  const totalAccessories = semaforo?.length ?? 0;
  const redCount = semaforo?.filter((a) => a.semaforo_status === 'ROJO').length ?? 0;
  const yellowCount = semaforo?.filter((a) => a.semaforo_status === 'AMARILLO').length ?? 0;
  const greenCount = semaforo?.filter((a) => a.semaforo_status === 'VERDE').length ?? 0;

  return (
    <div className="flex-1 overflow-auto p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard title="Proyectos Activos" value={activeProjects}
          icon={<FolderKanban className="text-blue-600" size={28} />}
          bg="from-blue-50 to-blue-100" border="border-blue-200" text="text-blue-600"
        />
        <StatCard title="Accesorios" value={totalAccessories}
          icon={<Wrench className="text-indigo-600" size={28} />}
          bg="from-indigo-50 to-indigo-100" border="border-indigo-200" text="text-indigo-600"
        />
        <StatCard title="Alertas Rojas" value={redCount}
          icon={<AlertTriangle className="text-red-600" size={28} />}
          bg="from-red-50 to-red-100" border="border-red-200" text="text-red-600"
        />
        <StatCard title="Alertas Amarillas" value={yellowCount}
          icon={<AlertTriangle className="text-yellow-600" size={28} />}
          bg="from-yellow-50 to-yellow-100" border="border-yellow-200" text="text-yellow-600"
        />
      </div>

      {totalAccessories > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <BarChart3 size={20} /> Resumen Semáforo
          </h3>
          <div className="flex rounded-lg overflow-hidden h-8">
            {greenCount > 0 && (
              <div className="bg-green-500 flex items-center justify-center text-white text-xs font-medium"
                style={{ width: `${(greenCount / totalAccessories) * 100}%` }}>{greenCount}</div>
            )}
            {yellowCount > 0 && (
              <div className="bg-yellow-400 flex items-center justify-center text-gray-900 text-xs font-medium"
                style={{ width: `${(yellowCount / totalAccessories) * 100}%` }}>{yellowCount}</div>
            )}
            {redCount > 0 && (
              <div className="bg-red-500 flex items-center justify-center text-white text-xs font-medium"
                style={{ width: `${(redCount / totalAccessories) * 100}%` }}>{redCount}</div>
            )}
          </div>
          <div className="flex gap-6 mt-3 text-sm">
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-green-500" /> Verde: {greenCount}</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-yellow-400" /> Amarillo: {yellowCount}</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-red-500" /> Rojo: {redCount}</span>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Sistema de Gestión de Accesorios de Izaje</h3>
        <p className="text-gray-500 text-sm">v1.2.1</p>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, bg, border, text }: {
  title: string; value: number; icon: React.ReactNode; bg: string; border: string; text: string;
}) {
  return (
    <div className={`bg-gradient-to-br ${bg} rounded-lg p-5 border ${border}`}>
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-gray-800">{title}</h4>
        {icon}
      </div>
      <p className={`text-3xl font-bold ${text}`}>{value}</p>
    </div>
  );
}
