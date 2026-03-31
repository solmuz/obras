import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { accessoriesApi } from '@/services/accessoriesApi';
import { projectsApi } from '@/services/projectsApi';
import { useAuthStore } from '@/store/authStore';
import { AccessoryCreate, AccessoryStatus, ElementType } from '@/types';
import { Plus, Search, Wrench } from 'lucide-react';
import { Dialog } from '@headlessui/react';

export default function AccessoriesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const { user } = useAuthStore();
  const canWrite = user?.role === 'ADMIN' || user?.role === 'INGENIERO_HSE';

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<AccessoryStatus | ''>('');
  const [typeFilter, setTypeFilter] = useState<ElementType | ''>('');
  const [projectFilter, setProjectFilter] = useState(searchParams.get('project_id') ?? '');
  const [showCreate, setShowCreate] = useState(searchParams.has('new'));
  const [form, setForm] = useState<AccessoryCreate>({
    code_internal: '',
    element_type: 'ESLINGAS',
    brand: 'BRAND_1',
    serial: '',
    material: '',
    project_id: searchParams.get('project_id') ?? '',
  });

  const { data: accessories, isLoading } = useQuery({
    queryKey: ['accessories', statusFilter, typeFilter, projectFilter],
    queryFn: () => accessoriesApi.listAccessories({
      ...(statusFilter && { status: statusFilter }),
      ...(typeFilter && { element_type: typeFilter }),
      ...(projectFilter && { project_id: projectFilter }),
    }),
  });

  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.listProjects(),
  });

  const createMutation = useMutation({
    mutationFn: (data: AccessoryCreate) => accessoriesApi.createAccessory(data),
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ['accessories'] });
      setShowCreate(false);
      navigate(`/accessories/${created.id}`);
    },
  });

  const filtered = accessories?.filter((a) =>
    a.code_internal.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="flex-1 overflow-auto p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Wrench size={24} /> Accesorios
        </h2>
        {canWrite && (
          <button onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition">
            <Plus size={18} /> Nuevo Accesorio
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por código..." className="w-full pl-10 pr-4 py-2 border rounded-lg" />
        </div>
        <select value={projectFilter} onChange={(e) => setProjectFilter(e.target.value)}
          className="border rounded-lg px-4 py-2">
          <option value="">Todos los proyectos</option>
          {projects?.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value as AccessoryStatus | '')}
          className="border rounded-lg px-4 py-2">
          <option value="">Todos los estados</option>
          <option value="EN_USO">En Uso</option>
          <option value="EN_STOCK">En Stock</option>
          <option value="TAG_ROJO">Tag Rojo</option>
        </select>
        <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value as ElementType | '')}
          className="border rounded-lg px-4 py-2">
          <option value="">Todos los tipos</option>
          <option value="ESLINGAS">Eslingas</option>
          <option value="GRILLETES">Grilletes</option>
          <option value="GANCHOS">Ganchos</option>
          <option value="OTROS">Otros</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Código</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Tipo</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Marca</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Semáforo</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {isLoading ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-400">Cargando...</td></tr>
            ) : filtered?.length === 0 ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-400">Sin accesorios</td></tr>
            ) : (
              filtered?.map((a) => (
                <tr key={a.id} onClick={() => navigate(`/accessories/${a.id}`)}
                  className="hover:bg-gray-50 cursor-pointer transition">
                  <td className="px-6 py-4 font-medium text-gray-900">{a.code_internal}</td>
                  <td className="px-6 py-4 text-gray-600">{a.element_type}</td>
                  <td className="px-6 py-4 text-gray-600">{a.brand}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      a.status === 'EN_USO' ? 'bg-green-100 text-green-700' :
                      a.status === 'EN_STOCK' ? 'bg-blue-100 text-blue-700' : 'bg-red-100 text-red-700'
                    }`}>{a.status.replace('_', ' ')}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`w-4 h-4 rounded-full inline-block ${
                      a.semaforo_status === 'VERDE' ? 'bg-green-500' :
                      a.semaforo_status === 'AMARILLO' ? 'bg-yellow-400' : 'bg-red-500'
                    }`} />
                  </td>
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
          <Dialog.Panel className="bg-white rounded-lg shadow-xl p-6 w-full max-w-lg max-h-[90vh] overflow-auto">
            <Dialog.Title className="text-lg font-semibold mb-4">Nuevo Accesorio</Dialog.Title>
            <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate(form); }} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Código Interno *</label>
                  <input value={form.code_internal} onChange={(e) => setForm({ ...form, code_internal: e.target.value })}
                    required className="w-full border rounded-lg px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Serial *</label>
                  <input value={form.serial} onChange={(e) => setForm({ ...form, serial: e.target.value })}
                    required className="w-full border rounded-lg px-3 py-2" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Elemento *</label>
                  <select value={form.element_type} onChange={(e) => setForm({ ...form, element_type: e.target.value as ElementType })}
                    className="w-full border rounded-lg px-3 py-2">
                    <option value="ESLINGAS">Eslingas</option>
                    <option value="GRILLETES">Grilletes</option>
                    <option value="GANCHOS">Ganchos</option>
                    <option value="OTROS">Otros</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Marca *</label>
                  <select value={form.brand} onChange={(e) => setForm({ ...form, brand: e.target.value as 'BRAND_1' | 'BRAND_2' | 'BRAND_3' })}
                    className="w-full border rounded-lg px-3 py-2">
                    <option value="BRAND_1">Brand 1</option>
                    <option value="BRAND_2">Brand 2</option>
                    <option value="BRAND_3">Brand 3</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Material *</label>
                <input value={form.material} onChange={(e) => setForm({ ...form, material: e.target.value })}
                  required className="w-full border rounded-lg px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Proyecto *</label>
                <select value={form.project_id} onChange={(e) => setForm({ ...form, project_id: e.target.value })}
                  required className="w-full border rounded-lg px-3 py-2">
                  <option value="">Seleccionar proyecto</option>
                  {projects?.filter((p) => p.status === 'ACTIVO').map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Cap. Vertical</label>
                  <input value={form.capacity_vertical ?? ''} onChange={(e) => setForm({ ...form, capacity_vertical: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Cap. Choker</label>
                  <input value={form.capacity_choker ?? ''} onChange={(e) => setForm({ ...form, capacity_choker: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Cap. Basket</label>
                  <input value={form.capacity_basket ?? ''} onChange={(e) => setForm({ ...form, capacity_basket: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2" />
                </div>
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
