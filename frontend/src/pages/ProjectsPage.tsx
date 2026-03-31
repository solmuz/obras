import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { projectsApi } from '@/services/projectsApi';
import { useAuthStore } from '@/store/authStore';
import { ProjectCreate, ProjectStatus } from '@/types';
import { Plus, Search, FolderKanban } from 'lucide-react';
import { Dialog } from '@headlessui/react';
import { formatDateShort } from '@/utils/dateUtils';

export default function ProjectsPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const canWrite = user?.role === 'ADMIN' || user?.role === 'INGENIERO_HSE';

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<ProjectStatus | ''>('');
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState<ProjectCreate>({ name: '', description: '', start_date: new Date().toISOString().slice(0, 10) });

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects', statusFilter],
    queryFn: () => projectsApi.listProjects(statusFilter ? { status: statusFilter } : undefined),
  });

  const createMutation = useMutation({
    mutationFn: (data: ProjectCreate) => projectsApi.createProject(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setShowCreate(false);
      setForm({ name: '', description: '', start_date: new Date().toISOString().slice(0, 10) });
    },
  });

  const filtered = projects?.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="flex-1 overflow-auto p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <FolderKanban size={24} /> Proyectos
        </h2>
        {canWrite && (
          <button onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition">
            <Plus size={18} /> Nuevo Proyecto
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar proyecto..." className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value as ProjectStatus | '')}
          className="border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500">
          <option value="">Todos</option>
          <option value="ACTIVO">Activo</option>
          <option value="INACTIVO">Inactivo</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Nombre</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Inicio</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Empleados</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Accesorios</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {isLoading ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-400">Cargando...</td></tr>
            ) : filtered?.length === 0 ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-400">Sin proyectos</td></tr>
            ) : (
              filtered?.map((p) => (
                <tr key={p.id} onClick={() => navigate(`/projects/${p.id}`)}
                  className="hover:bg-gray-50 cursor-pointer transition">
                  <td className="px-6 py-4 font-medium text-gray-900">{p.name}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      p.status === 'ACTIVO' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                    }`}>{p.status}</span>
                  </td>
                  <td className="px-6 py-4 text-gray-600 text-sm">{formatDateShort(p.start_date)}</td>
                  <td className="px-6 py-4 text-gray-600">{p.employee_count}</td>
                  <td className="px-6 py-4 text-gray-600">{p.accessory_count}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create Dialog */}
      <Dialog open={showCreate} onClose={() => setShowCreate(false)} className="relative z-50">
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Dialog.Panel className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <Dialog.Title className="text-lg font-semibold mb-4">Nuevo Proyecto</Dialog.Title>
            <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate(form); }} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                <textarea value={form.description ?? ''} onChange={(e) => setForm({ ...form, description: e.target.value })}
                  rows={3} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de inicio *</label>
                <input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })}
                  required className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500" />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowCreate(false)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancelar</button>
                <button type="submit" disabled={createMutation.isPending}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                  {createMutation.isPending ? 'Creando...' : 'Crear'}
                </button>
              </div>
              {createMutation.isError && (
                <p className="text-red-600 text-sm">{(createMutation.error as any)?.response?.data?.detail ?? 'Error al crear'}</p>
              )}
            </form>
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  );
}
