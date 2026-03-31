import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { auditApi } from '@/services/auditApi';
import { useAuthStore } from '@/store/authStore';
import { ClipboardList } from 'lucide-react';
import { formatDateInTZ } from '@/utils/dateUtils';

export default function AuditPage() {
  const { user } = useAuthStore();
  const isAdmin = user?.role === 'ADMIN';
  const [entityFilter, setEntityFilter] = useState('');
  const [actionFilter, setActionFilter] = useState('');

  const { data: logs, isLoading } = useQuery({
    queryKey: ['audit-logs', entityFilter, actionFilter],
    queryFn: () => auditApi.list({
      ...(entityFilter && { entity_type: entityFilter }),
      ...(actionFilter && { action: actionFilter }),
      limit: 100,
    }),
    enabled: isAdmin,
  });

  if (!isAdmin) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-gray-500">No tienes permisos para ver esta página</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-auto p-8">
      <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2 mb-6">
        <ClipboardList size={24} /> Registro de Auditoría
      </h2>

      <div className="flex gap-4 mb-6">
        <select value={entityFilter} onChange={(e) => setEntityFilter(e.target.value)}
          className="border rounded-lg px-4 py-2">
          <option value="">Todas las entidades</option>
          <option value="project">Proyectos</option>
          <option value="accessory">Accesorios</option>
          <option value="user">Usuarios</option>
          <option value="external_inspection">Insp. Externas</option>
          <option value="site_inspection">Insp. Sitio</option>
          <option value="decommission">Bajas</option>
        </select>
        <select value={actionFilter} onChange={(e) => setActionFilter(e.target.value)}
          className="border rounded-lg px-4 py-2">
          <option value="">Todas las acciones</option>
          <option value="CREATE">Crear</option>
          <option value="UPDATE">Actualizar</option>
          <option value="DELETE">Eliminar</option>
        </select>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Fecha</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Acción</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Entidad</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Descripción</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {isLoading ? (
              <tr><td colSpan={4} className="px-6 py-8 text-center text-gray-400">Cargando...</td></tr>
            ) : logs?.length === 0 ? (
              <tr><td colSpan={4} className="px-6 py-8 text-center text-gray-400">Sin registros</td></tr>
            ) : (
              logs?.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-600">{formatDateInTZ(log.created_at)}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      log.action === 'CREATE' ? 'bg-green-100 text-green-700' :
                      log.action === 'UPDATE' ? 'bg-blue-100 text-blue-700' : 'bg-red-100 text-red-700'
                    }`}>{log.action}</span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{log.entity_type}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{log.change_description ?? '-'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
