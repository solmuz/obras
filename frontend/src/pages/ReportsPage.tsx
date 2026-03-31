import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { reportsApi } from '@/services/reportsApi';
import { projectsApi } from '@/services/projectsApi';
import { BarChart3, Download } from 'lucide-react';

export default function ReportsPage() {
  const navigate = useNavigate();
  const [projectFilter, setProjectFilter] = useState('');
  const [semaforoFilter, setSemaforoFilter] = useState('');

  const { data: accessories, isLoading } = useQuery({
    queryKey: ['semaforo', projectFilter, semaforoFilter],
    queryFn: () => reportsApi.getSemaforo({
      ...(projectFilter && { project_id: projectFilter }),
      ...(semaforoFilter && { semaforo_status: semaforoFilter }),
    }),
  });

  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.listProjects(),
  });

  const handleExportPdf = async () => {
    try {
      const blob = await reportsApi.exportPdf({
        ...(projectFilter && { project_id: projectFilter }),
        ...(semaforoFilter && { semaforo_status: semaforoFilter }),
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'reporte-semaforo.pdf';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      alert('Error al generar PDF');
    }
  };

  const verde = accessories?.filter((a) => a.semaforo_status === 'VERDE') ?? [];
  const amarillo = accessories?.filter((a) => a.semaforo_status === 'AMARILLO') ?? [];
  const rojo = accessories?.filter((a) => a.semaforo_status === 'ROJO') ?? [];

  return (
    <div className="flex-1 overflow-auto p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <BarChart3 size={24} /> Semáforo de Inspecciones
        </h2>
        <button onClick={handleExportPdf}
          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-900 text-white px-4 py-2 rounded-lg">
          <Download size={18} /> Exportar PDF
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <select value={projectFilter} onChange={(e) => setProjectFilter(e.target.value)}
          className="border rounded-lg px-4 py-2">
          <option value="">Todos los proyectos</option>
          {projects?.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        <select value={semaforoFilter} onChange={(e) => setSemaforoFilter(e.target.value)}
          className="border rounded-lg px-4 py-2">
          <option value="">Todos los estados</option>
          <option value="VERDE">Verde</option>
          <option value="AMARILLO">Amarillo</option>
          <option value="ROJO">Rojo</option>
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
          <div className="w-6 h-6 rounded-full bg-green-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-green-700">{verde.length}</p>
          <p className="text-green-600 text-sm">Verde - Al día</p>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
          <div className="w-6 h-6 rounded-full bg-yellow-400 mx-auto mb-2" />
          <p className="text-2xl font-bold text-yellow-700">{amarillo.length}</p>
          <p className="text-yellow-600 text-sm">Amarillo - Por vencer</p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
          <div className="w-6 h-6 rounded-full bg-red-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-red-700">{rojo.length}</p>
          <p className="text-red-600 text-sm">Rojo - Vencido</p>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Semáforo</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Código</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Tipo</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Marca</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {isLoading ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-400">Cargando...</td></tr>
            ) : accessories?.length === 0 ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-400">Sin accesorios</td></tr>
            ) : (
              accessories?.map((a) => (
                <tr key={a.id} onClick={() => navigate(`/accessories/${a.id}`)}
                  className="hover:bg-gray-50 cursor-pointer transition">
                  <td className="px-6 py-4">
                    <span className={`w-5 h-5 rounded-full inline-block ${
                      a.semaforo_status === 'VERDE' ? 'bg-green-500' :
                      a.semaforo_status === 'AMARILLO' ? 'bg-yellow-400' : 'bg-red-500'
                    }`} />
                  </td>
                  <td className="px-6 py-4 font-medium text-gray-900">{a.code_internal}</td>
                  <td className="px-6 py-4 text-gray-600">{a.element_type}</td>
                  <td className="px-6 py-4 text-gray-600">{a.brand}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      a.status === 'EN_USO' ? 'bg-green-100 text-green-700' :
                      a.status === 'EN_STOCK' ? 'bg-blue-100 text-blue-700' : 'bg-red-100 text-red-700'
                    }`}>{a.status.replace('_', ' ')}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
