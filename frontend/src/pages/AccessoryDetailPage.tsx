import { useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { accessoriesApi } from '@/services/accessoriesApi';
import { externalInspectionsApi, siteInspectionsApi } from '@/services/inspectionsApi';
import { decommissionsApi } from '@/services/decommissionsApi';
import { useAuthStore } from '@/store/authStore';
import { AccessoryUpdate, ExternalInspectionCreate, SiteInspectionCreate, DecommissionCreate } from '@/types';
import { ArrowLeft, Edit2, Trash2, Upload, FileText, ClipboardCheck } from 'lucide-react';
import { Dialog } from '@headlessui/react';
import { useDropzone } from 'react-dropzone';
import { formatDateShort } from '@/utils/dateUtils';

type InspectionTab = 'external' | 'site' | 'decommissions';

export default function AccessoryDetailPage() {
  const { accessoryId } = useParams<{ accessoryId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const canWrite = user?.role === 'ADMIN' || user?.role === 'INGENIERO_HSE';
  const isAdmin = user?.role === 'ADMIN';

  const [tab, setTab] = useState<InspectionTab>('external');
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState<AccessoryUpdate>({});
  const [showExtCreate, setShowExtCreate] = useState(false);
  const [showSiteCreate, setShowSiteCreate] = useState(false);
  const [showDecom, setShowDecom] = useState(false);

  const { data: accessory, isLoading } = useQuery({
    queryKey: ['accessory', accessoryId],
    queryFn: () => accessoriesApi.getAccessory(accessoryId!),
    enabled: !!accessoryId,
  });

  const { data: extInspections } = useQuery({
    queryKey: ['ext-inspections', accessoryId],
    queryFn: () => externalInspectionsApi.list({ accessory_id: accessoryId }),
    enabled: !!accessoryId,
  });

  const { data: siteInspections } = useQuery({
    queryKey: ['site-inspections', accessoryId],
    queryFn: () => siteInspectionsApi.list({ accessory_id: accessoryId }),
    enabled: !!accessoryId,
  });

  const { data: decomRecords } = useQuery({
    queryKey: ['decommissions', accessoryId],
    queryFn: () => decommissionsApi.list({ accessory_id: accessoryId }),
    enabled: !!accessoryId,
  });

  const updateMutation = useMutation({
    mutationFn: (data: AccessoryUpdate) => accessoriesApi.updateAccessory(accessoryId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accessory', accessoryId] });
      setEditing(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => accessoriesApi.deleteAccessory(accessoryId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accessories'] });
      navigate('/accessories');
    },
  });

  const photoMutation = useMutation({
    mutationFn: ({ file, type }: { file: File; type: 'accessory' | 'manufacturer_label' | 'provider_marking' }) =>
      accessoriesApi.uploadPhoto(accessoryId!, file, type),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['accessory', accessoryId] }),
  });

  const extCreateMutation = useMutation({
    mutationFn: (data: ExternalInspectionCreate) => externalInspectionsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ext-inspections', accessoryId] });
      queryClient.invalidateQueries({ queryKey: ['accessory', accessoryId] });
      setShowExtCreate(false);
    },
  });

  const siteCreateMutation = useMutation({
    mutationFn: (data: SiteInspectionCreate) => siteInspectionsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['site-inspections', accessoryId] });
      queryClient.invalidateQueries({ queryKey: ['accessory', accessoryId] });
      setShowSiteCreate(false);
    },
  });

  const decomCreateMutation = useMutation({
    mutationFn: (data: DecommissionCreate) => decommissionsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decommissions', accessoryId] });
      queryClient.invalidateQueries({ queryKey: ['accessory', accessoryId] });
      setShowDecom(false);
    },
  });

  if (isLoading) return <div className="p-8 text-gray-400">Cargando...</div>;
  if (!accessory) return <div className="p-8 text-red-500">Accesorio no encontrado</div>;

  const semaforoColor = accessory.semaforo_status === 'VERDE' ? 'bg-green-500' :
    accessory.semaforo_status === 'AMARILLO' ? 'bg-yellow-400' : 'bg-red-500';

  return (
    <div className="flex-1 overflow-auto p-8">
      <button onClick={() => navigate('/accessories')} className="flex items-center gap-1 text-gray-500 hover:text-gray-700 mb-4">
        <ArrowLeft size={18} /> Volver a accesorios
      </button>

      {/* Info Card */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <h2 className="text-2xl font-bold text-gray-900">{accessory.code_internal}</h2>
              <span className={`w-5 h-5 rounded-full ${semaforoColor}`} title={accessory.semaforo_status} />
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                accessory.status === 'EN_USO' ? 'bg-green-100 text-green-700' :
                accessory.status === 'EN_STOCK' ? 'bg-blue-100 text-blue-700' : 'bg-red-100 text-red-700'
              }`}>{accessory.status.replace('_', ' ')}</span>
            </div>
            {editing ? (
              <form onSubmit={(e) => { e.preventDefault(); updateMutation.mutate(editForm); }} className="space-y-3">
                <select value={editForm.status ?? accessory.status}
                  onChange={(e) => setEditForm({ ...editForm, status: e.target.value as any })}
                  className="border rounded px-2 py-1 text-sm">
                  <option value="EN_USO">En Uso</option>
                  <option value="EN_STOCK">En Stock</option>
                  <option value="TAG_ROJO">Tag Rojo</option>
                </select>
                <div className="flex gap-2">
                  <button type="submit" className="px-3 py-1 bg-blue-600 text-white rounded text-sm">Guardar</button>
                  <button type="button" onClick={() => setEditing(false)} className="px-3 py-1 bg-gray-200 rounded text-sm">Cancelar</button>
                </div>
              </form>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <InfoField label="Tipo" value={accessory.element_type} />
                <InfoField label="Marca" value={accessory.brand} />
                <InfoField label="Serial" value={accessory.serial} />
                <InfoField label="Material" value={accessory.material} />
                <InfoField label="Cap. Vertical" value={accessory.capacity_vertical ?? '-'} />
                <InfoField label="Cap. Choker" value={accessory.capacity_choker ?? '-'} />
                <InfoField label="Cap. Basket" value={accessory.capacity_basket ?? '-'} />
                <InfoField label="Longitud (m)" value={accessory.length_m?.toString() ?? '-'} />
              </div>
            )}
          </div>
          {canWrite && !editing && (
            <div className="flex gap-2">
              <button onClick={() => { setEditForm({ status: accessory.status }); setEditing(true); }}
                className="p-2 text-gray-500 hover:bg-gray-100 rounded"><Edit2 size={18} /></button>
              {isAdmin && (
                <button onClick={() => { if (confirm('¿Eliminar este accesorio?')) deleteMutation.mutate(); }}
                  className="p-2 text-red-500 hover:bg-red-50 rounded"><Trash2 size={18} /></button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Photos */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">Fotos</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <PhotoSlot label="Accesorio" url={accessory.photo_accessory}
            onUpload={canWrite ? (f) => photoMutation.mutate({ file: f, type: 'accessory' }) : undefined} />
          <PhotoSlot label="Etiqueta Fabricante" url={accessory.photo_manufacturer_label}
            onUpload={canWrite ? (f) => photoMutation.mutate({ file: f, type: 'manufacturer_label' }) : undefined} />
          <PhotoSlot label="Marcación Proveedor" url={accessory.photo_provider_marking}
            onUpload={canWrite ? (f) => photoMutation.mutate({ file: f, type: 'provider_marking' }) : undefined} />
        </div>
      </div>

      {/* Inspection Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b flex">
          <TabButton active={tab === 'external'} onClick={() => setTab('external')} icon={<FileText size={16} />}
            label={`Ext. (${extInspections?.length ?? 0})`} />
          <TabButton active={tab === 'site'} onClick={() => setTab('site')} icon={<ClipboardCheck size={16} />}
            label={`Sitio (${siteInspections?.length ?? 0})`} />
          <TabButton active={tab === 'decommissions'} onClick={() => setTab('decommissions')} icon={<Trash2 size={16} />}
            label={`Baja (${decomRecords?.length ?? 0})`} />
          <div className="flex-1" />
          {canWrite && tab === 'external' && (
            <button onClick={() => setShowExtCreate(true)} className="px-4 py-2 text-sm text-blue-600 hover:bg-blue-50">+ Inspección Externa</button>
          )}
          {canWrite && tab === 'site' && (
            <button onClick={() => setShowSiteCreate(true)} className="px-4 py-2 text-sm text-blue-600 hover:bg-blue-50">+ Inspección Sitio</button>
          )}
          {canWrite && tab === 'decommissions' && (
            <button onClick={() => setShowDecom(true)} className="px-4 py-2 text-sm text-blue-600 hover:bg-blue-50">+ Dar de Baja</button>
          )}
        </div>

        <div className="p-6">
          {tab === 'external' && (
            extInspections?.length === 0 ? <p className="text-gray-400">Sin inspecciones externas</p> : (
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Fecha</th>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Empresa</th>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Responsable</th>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Próxima</th>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Estado</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {extInspections?.map((i) => (
                    <tr key={i.id}>
                      <td className="px-4 py-2 text-sm">{formatDateShort(i.inspection_date)}</td>
                      <td className="px-4 py-2 text-sm">{i.company}</td>
                      <td className="px-4 py-2 text-sm">{i.company_responsible}</td>
                      <td className="px-4 py-2 text-sm">{formatDateShort(i.next_inspection_date)}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-0.5 rounded-full text-xs ${
                          i.status === 'VIGENTE' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        }`}>{i.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          )}

          {tab === 'site' && (
            siteInspections?.length === 0 ? <p className="text-gray-400">Sin inspecciones de sitio</p> : (
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Fecha</th>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Período</th>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Criterio</th>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Inspector</th>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Estado</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {siteInspections?.map((i) => (
                    <tr key={i.id}>
                      <td className="px-4 py-2 text-sm">{formatDateShort(i.inspection_date)}</td>
                      <td className="px-4 py-2 text-sm">{i.color_period}</td>
                      <td className="px-4 py-2 text-sm">
                        <span className={`px-2 py-0.5 rounded-full text-xs ${
                          i.final_criterion === 'BUEN_ESTADO' ? 'bg-green-100 text-green-700' :
                          i.final_criterion === 'MAL_ESTADO' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
                        }`}>{i.final_criterion.replace('_', ' ')}</span>
                      </td>
                      <td className="px-4 py-2 text-sm">{i.inspector_name}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-0.5 rounded-full text-xs ${
                          i.status === 'VIGENTE' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        }`}>{i.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          )}

          {tab === 'decommissions' && (
            decomRecords?.length === 0 ? <p className="text-gray-400">Sin registros de baja</p> : (
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Fecha</th>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Razón</th>
                    <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Responsable</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {decomRecords?.map((d) => (
                    <tr key={d.id}>
                      <td className="px-4 py-2 text-sm">{formatDateShort(d.decommission_date)}</td>
                      <td className="px-4 py-2 text-sm">{d.reason}</td>
                      <td className="px-4 py-2 text-sm">{d.responsible_name}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          )}
        </div>
      </div>

      {/* Create External Inspection Dialog */}
      <CreateExtDialog open={showExtCreate} onClose={() => setShowExtCreate(false)}
        accessoryId={accessoryId!} mutation={extCreateMutation} />

      {/* Create Site Inspection Dialog */}
      <CreateSiteDialog open={showSiteCreate} onClose={() => setShowSiteCreate(false)}
        accessoryId={accessoryId!} mutation={siteCreateMutation} />

      {/* Create Decommission Dialog */}
      <CreateDecomDialog open={showDecom} onClose={() => setShowDecom(false)}
        accessoryId={accessoryId!} mutation={decomCreateMutation} />
    </div>
  );
}

function InfoField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="text-gray-500 text-xs">{label}</span>
      <p className="font-medium text-gray-900">{value}</p>
    </div>
  );
}

function PhotoSlot({ label, url, onUpload }: { label: string; url?: string; onUpload?: (f: File) => void }) {
  const onDrop = useCallback((files: File[]) => {
    if (files[0] && onUpload) onUpload(files[0]);
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'image/*': [] }, maxFiles: 1, disabled: !onUpload,
  });

  return (
    <div className="border rounded-lg overflow-hidden">
      <p className="text-xs font-medium text-gray-500 px-3 py-2 bg-gray-50">{label}</p>
      {url ? (
        <div className="relative group">
          <img src={url} alt={label} className="w-full h-40 object-cover" />
          {onUpload && (
            <div {...getRootProps()} className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center cursor-pointer transition">
              <input {...getInputProps()} />
              <Upload className="text-white" size={24} />
            </div>
          )}
        </div>
      ) : (
        <div {...getRootProps()} className={`h-40 flex flex-col items-center justify-center text-gray-400 ${
          onUpload ? 'cursor-pointer hover:bg-gray-50' : ''
        } ${isDragActive ? 'bg-blue-50 border-blue-300' : ''}`}>
          <input {...getInputProps()} />
          <Upload size={24} />
          <span className="text-xs mt-1">{onUpload ? 'Subir foto' : 'Sin foto'}</span>
        </div>
      )}
    </div>
  );
}

function TabButton({ active, onClick, icon, label }: { active: boolean; onClick: () => void; icon: React.ReactNode; label: string }) {
  return (
    <button onClick={onClick} className={`flex items-center gap-1 px-4 py-3 text-sm font-medium border-b-2 transition ${
      active ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
    }`}>{icon} {label}</button>
  );
}

function CreateExtDialog({ open, onClose, accessoryId, mutation }: {
  open: boolean; onClose: () => void; accessoryId: string; mutation: any;
}) {
  const [form, setForm] = useState<ExternalInspectionCreate>({
    accessory_id: accessoryId, inspection_date: '', company: 'GEO',
    company_responsible: '', final_criterion: '', project_name: '', equipment_status: '',
  });

  return (
    <Dialog open={open} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
          <Dialog.Title className="text-lg font-semibold mb-4">Nueva Inspección Externa</Dialog.Title>
          <form onSubmit={(e) => { e.preventDefault(); mutation.mutate({ ...form, accessory_id: accessoryId }); }} className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fecha *</label>
              <input type="date" value={form.inspection_date}
                onChange={(e) => setForm({ ...form, inspection_date: e.target.value })}
                required className="w-full border rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Empresa *</label>
              <select value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value as any })}
                className="w-full border rounded-lg px-3 py-2">
                <option value="GEO">GEO</option>
                <option value="SBCIMAS">SBCIMAS</option>
                <option value="PREFA">PREFA</option>
                <option value="BESSAC">BESSAC</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Responsable *</label>
              <input value={form.company_responsible}
                onChange={(e) => setForm({ ...form, company_responsible: e.target.value })}
                required className="w-full border rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Criterio Final *</label>
              <input value={form.final_criterion}
                onChange={(e) => setForm({ ...form, final_criterion: e.target.value })}
                required className="w-full border rounded-lg px-3 py-2" />
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button type="button" onClick={onClose} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancelar</button>
              <button type="submit" disabled={mutation.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">Crear</button>
            </div>
          </form>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
}

function CreateSiteDialog({ open, onClose, accessoryId, mutation }: {
  open: boolean; onClose: () => void; accessoryId: string; mutation: any;
}) {
  const [form, setForm] = useState<SiteInspectionCreate>({
    accessory_id: accessoryId, inspection_date: '', final_criterion: 'BUEN_ESTADO',
    inspector_name: '', company: 'GEO', project_name: '', equipment_status: '',
  });

  return (
    <Dialog open={open} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
          <Dialog.Title className="text-lg font-semibold mb-4">Nueva Inspección de Sitio</Dialog.Title>
          <form onSubmit={(e) => { e.preventDefault(); mutation.mutate({ ...form, accessory_id: accessoryId }); }} className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fecha *</label>
              <input type="date" value={form.inspection_date}
                onChange={(e) => setForm({ ...form, inspection_date: e.target.value })}
                required className="w-full border rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Criterio Final *</label>
              <select value={form.final_criterion}
                onChange={(e) => setForm({ ...form, final_criterion: e.target.value as any })}
                className="w-full border rounded-lg px-3 py-2">
                <option value="BUEN_ESTADO">Buen Estado</option>
                <option value="MAL_ESTADO">Mal Estado</option>
                <option value="OBSERVACIONES">Observaciones</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Inspector *</label>
              <input value={form.inspector_name}
                onChange={(e) => setForm({ ...form, inspector_name: e.target.value })}
                required className="w-full border rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Empresa *</label>
              <select value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value as any })}
                className="w-full border rounded-lg px-3 py-2">
                <option value="GEO">GEO</option>
                <option value="SBCIMAS">SBCIMAS</option>
                <option value="PREFA">PREFA</option>
                <option value="BESSAC">BESSAC</option>
              </select>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button type="button" onClick={onClose} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancelar</button>
              <button type="submit" disabled={mutation.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">Crear</button>
            </div>
          </form>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
}

function CreateDecomDialog({ open, onClose, accessoryId, mutation }: {
  open: boolean; onClose: () => void; accessoryId: string; mutation: any;
}) {
  const [form, setForm] = useState<DecommissionCreate>({
    accessory_id: accessoryId, decommission_date: '', reason: '', responsible_name: '',
  });

  return (
    <Dialog open={open} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
          <Dialog.Title className="text-lg font-semibold mb-4">Dar de Baja</Dialog.Title>
          <form onSubmit={(e) => { e.preventDefault(); mutation.mutate({ ...form, accessory_id: accessoryId }); }} className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fecha *</label>
              <input type="date" value={form.decommission_date}
                onChange={(e) => setForm({ ...form, decommission_date: e.target.value })}
                required className="w-full border rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Razón *</label>
              <textarea value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })}
                required rows={3} className="w-full border rounded-lg px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Responsable *</label>
              <input value={form.responsible_name}
                onChange={(e) => setForm({ ...form, responsible_name: e.target.value })}
                required className="w-full border rounded-lg px-3 py-2" />
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button type="button" onClick={onClose} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">Cancelar</button>
              <button type="submit" disabled={mutation.isPending}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50">Dar de Baja</button>
            </div>
          </form>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
}
