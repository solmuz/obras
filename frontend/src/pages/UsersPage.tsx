import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi } from '@/services/usersApi';
import { useAuthStore } from '@/store/authStore';
import { UserCreate } from '@/types';
import { Plus, Users, Search } from 'lucide-react';
import { Dialog } from '@headlessui/react';

export default function UsersPage() {
  const queryClient = useQueryClient();
  const { user: currentUser } = useAuthStore();
  const isAdmin = currentUser?.role === 'ADMIN';

  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState<UserCreate>({ email: '', full_name: '', password: '', role: 'CONSULTA' });

  const { data: users, isLoading } = useQuery({
    queryKey: ['users', roleFilter],
    queryFn: () => usersApi.listUsers(roleFilter ? { role: roleFilter } : undefined),
  });

  const createMutation = useMutation({
    mutationFn: (data: UserCreate) => usersApi.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setShowCreate(false);
      setForm({ email: '', full_name: '', password: '', role: 'CONSULTA' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (userId: string) => usersApi.deleteUser(userId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  });

  const filtered = users?.filter((u) =>
    u.full_name.toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase()),
  );

  if (!isAdmin) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-gray-500">No tienes permisos para ver esta página</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-auto p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Users size={24} /> Usuarios
        </h2>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
          <Plus size={18} /> Nuevo Usuario
        </button>
      </div>

      <div className="flex gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por nombre o email..." className="w-full pl-10 pr-4 py-2 border rounded-lg" />
        </div>
        <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}
          className="border rounded-lg px-4 py-2">
          <option value="">Todos los roles</option>
          <option value="ADMIN">Admin</option>
          <option value="INGENIERO_HSE">Ingeniero HSE</option>
          <option value="CONSULTA">Consulta</option>
        </select>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Nombre</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Email</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Rol</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {isLoading ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-400">Cargando...</td></tr>
            ) : filtered?.length === 0 ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-400">Sin usuarios</td></tr>
            ) : (
              filtered?.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900">{u.full_name}</td>
                  <td className="px-6 py-4 text-gray-600">{u.email}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      u.role === 'ADMIN' ? 'bg-purple-100 text-purple-700' :
                      u.role === 'INGENIERO_HSE' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                    }`}>{u.role}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}>{u.is_active ? 'Activo' : 'Inactivo'}</span>
                  </td>
                  <td className="px-6 py-4">
                    {u.id !== currentUser?.id && (
                      <button onClick={() => { if (confirm(`¿Eliminar usuario ${u.full_name}?`)) deleteMutation.mutate(u.id); }}
                        className="text-red-500 hover:text-red-700 text-sm">Eliminar</button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create User Dialog */}
      <Dialog open={showCreate} onClose={() => setShowCreate(false)} className="relative z-50">
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Dialog.Panel className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <Dialog.Title className="text-lg font-semibold mb-4">Nuevo Usuario</Dialog.Title>
            <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate(form); }} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre Completo *</label>
                <input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  required className="w-full border rounded-lg px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
                  required className="w-full border rounded-lg px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña *</label>
                <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
                  required minLength={8} className="w-full border rounded-lg px-3 py-2" />
                <p className="text-xs text-gray-500 mt-1">Mín. 8 caracteres, mayúscula, minúscula, número y carácter especial</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Rol *</label>
                <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value as any })}
                  className="w-full border rounded-lg px-3 py-2">
                  <option value="CONSULTA">Consulta</option>
                  <option value="INGENIERO_HSE">Ingeniero HSE</option>
                  <option value="ADMIN">Admin</option>
                </select>
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
