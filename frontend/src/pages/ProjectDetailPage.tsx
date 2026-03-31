import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '@/services/projectsApi';
import { accessoriesApi } from '@/services/accessoriesApi';
import { usersApi } from '@/services/usersApi';
import { useAuthStore } from '@/store/authStore';
import { ProjectUpdate } from '@/types';
import { ArrowLeft, Edit2, Trash2, UserPlus, X } from 'lucide-react';
import { Dialog } from '@headlessui/react';
import { formatDateShort } from '@/utils/dateUtils';

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const canWrite = user?.role === 'ADMIN' || user?.role === 'INGENIERO_HSE';
  const isAdmin = user?.role === 'ADMIN';

  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState<ProjectUpdate>({});
  const [showAssign, setShowAssign] = useState(false);

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.getProject(projectId!),
    enabled: !!projectId,
  });

  const { data: accessories } = useQuery({
    queryKey: ['accessories', { project_id: projectId }],
    queryFn: () => accessoriesApi.listAccessories({ project_id: projectId }),
    enabled: !!projectId,
  });

  const { data: allUsers } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.listUsers(),
    enabled: showAssign,
  });

  const updateMutation = useMutation({
    mutationFn: (data: ProjectUpdate) => projectsApi.updateProject(projectId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setEditing(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => projectsApi.deleteProject(projectId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      navigate('/projects');
    },
  });

  const assignMutation = useMutation({
    mutationFn: (userId: string) => projectsApi.assignEmployee(projectId!, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      setShowAssign(false);
    },
  });

  const removeMutation = useMutation({
    mutationFn: (userId: string) => projectsApi.removeEmployee(projectId!, userId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['project', projectId] }),
  });

  if (isLoading) return <div className="p-8 text-gray-400">Cargando...</div>;
  if (!project) return <div className="p-8 text-red-500">Proyecto no encontrado</div>;

  const startEdit = () => {
    setEditForm({ name: project.name, description: project.description, status: project.status });
    setEditing(true);
  };

  const assignedIds = new Set(project.employees?.map((e) => e.id) ?? []);
  const unassignedUsers = allUsers?.filter((u) => !assignedIds.has(u.id) && u.is_active) ?? [];

  return (
    <div className="flex-1 overflow-auto p-8">
      <button onClick={() => navigate('/projects')} className="flex items-center gap-1 text-gray-500 hover:text-gray-700 mb-4">
        <ArrowLeft size={18} /> Volver a proyectos
      </button>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            {editing ? (
              <form onSubmit={(e) => { e.preventDefault(); updateMutation.mutate(editForm); }} className="space-y-3">
                <input value={editForm.name ?? ''} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                  className="text-2xl font-bold border-b-2 border-blue-500 focus:outline-none w-full" />
                <textarea value={editForm.description ?? ''} onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                  rows={2} className="w-full border rounded px-2 py-1 text-sm" />
                <select value={editForm.status ?? 'ACTIVO'}
                  onChange={(e) => setEditForm({ ...editForm, status: e.target.value as 'ACTIVO' | 'INACTIVO' })}
                  className="border rounded px-2 py-1 text-sm">
                  <option value="ACTIVO">Activo</option>
                  <option value="INACTIVO">Inactivo</option>
                </select>
                <div className="flex gap-2">
                  <button type="submit" className="px-3 py-1 bg-blue-600 text-white rounded text-sm">Guardar</button>
                  <button type="button" onClick={() => setEditing(false)} className="px-3 py-1 bg-gray-200 rounded text-sm">Cancelar</button>
                </div>
              </form>
            ) : (
              <>
                <h2 className="text-2xl font-bold text-gray-900">{project.name}</h2>
                <p className="text-gray-500 mt-1">{project.description || 'Sin descripción'}</p>
                <div className="flex gap-4 mt-3 text-sm">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    project.status === 'ACTIVO' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                  }`}>{project.status}</span>
                  <span className="text-gray-500">Inicio: {formatDateShort(project.start_date)}</span>
                </div>
              </>
            )}
          </div>
          {canWrite && !editing && (
            <div className="flex gap-2">
              <button onClick={startEdit} className="p-2 text-gray-500 hover:bg-gray-100 rounded"><Edit2 size={18} /></button>
              {isAdmin && (
                <button onClick={() => { if (confirm('¿Eliminar este proyecto?')) deleteMutation.mutate(); }}
                  className="p-2 text-red-500 hover:bg-red-50 rounded"><Trash2 size={18} /></button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Employees */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Empleados Asignados ({project.employees?.length ?? 0})</h3>
          {canWrite && (
            <button onClick={() => setShowAssign(true)}
              className="flex items-center gap-1 text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700">
              <UserPlus size={16} /> Asignar
            </button>
          )}
        </div>
        {project.employees?.length === 0 ? (
          <p className="text-gray-400 text-sm">Sin empleados asignados</p>
        ) : (
          <div className="space-y-2">
            {project.employees?.map((emp) => (
              <div key={emp.id} className="flex items-center justify-between bg-gray-50 rounded px-4 py-2">
                <div>
                  <span className="font-medium text-gray-900">{emp.full_name}</span>
                  <span className="text-gray-500 text-sm ml-2">{emp.email}</span>
                  <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">{emp.role}</span>
                </div>
                {canWrite && (
                  <button onClick={() => removeMutation.mutate(emp.id)}
                    className="text-red-500 hover:bg-red-50 p-1 rounded"><X size={16} /></button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Accessories */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Accesorios ({accessories?.length ?? 0})</h3>
          {canWrite && (
            <button onClick={() => navigate(`/accessories/new?project_id=${projectId}`)}
              className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700">
              + Nuevo Accesorio
            </button>
          )}
        </div>
        {!accessories?.length ? (
          <p className="text-gray-400 text-sm">Sin accesorios registrados</p>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Código</th>
                <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Tipo</th>
                <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Estado</th>
                <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Semáforo</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {accessories.map((a) => (
                <tr key={a.id} onClick={() => navigate(`/accessories/${a.id}`)}
                  className="hover:bg-gray-50 cursor-pointer">
                  <td className="px-4 py-2 font-medium">{a.code_internal}</td>
                  <td className="px-4 py-2 text-gray-600 text-sm">{a.element_type}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs ${
                      a.status === 'EN_USO' ? 'bg-green-100 text-green-700' :
                      a.status === 'EN_STOCK' ? 'bg-blue-100 text-blue-700' : 'bg-red-100 text-red-700'
                    }`}>{a.status}</span>
                  </td>
                  <td className="px-4 py-2">
                    <span className={`w-4 h-4 rounded-full inline-block ${
                      a.semaforo_status === 'VERDE' ? 'bg-green-500' :
                      a.semaforo_status === 'AMARILLO' ? 'bg-yellow-400' : 'bg-red-500'
                    }`} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Assign Employee Dialog */}
      <Dialog open={showAssign} onClose={() => setShowAssign(false)} className="relative z-50">
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Dialog.Panel className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <Dialog.Title className="text-lg font-semibold mb-4">Asignar Empleado</Dialog.Title>
            {unassignedUsers.length === 0 ? (
              <p className="text-gray-500">Todos los usuarios ya están asignados</p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-auto">
                {unassignedUsers.map((u) => (
                  <button key={u.id} onClick={() => assignMutation.mutate(u.id)}
                    disabled={assignMutation.isPending}
                    className="w-full text-left flex items-center justify-between px-4 py-2 bg-gray-50 hover:bg-blue-50 rounded transition">
                    <div>
                      <span className="font-medium">{u.full_name}</span>
                      <span className="text-gray-500 text-sm ml-2">{u.role}</span>
                    </div>
                    <UserPlus size={16} className="text-blue-600" />
                  </button>
                ))}
              </div>
            )}
            <div className="flex justify-end mt-4">
              <button onClick={() => setShowAssign(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cerrar</button>
            </div>
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  );
}
