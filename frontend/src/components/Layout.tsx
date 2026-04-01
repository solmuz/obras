import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import {
  Menu,
  LogOut,
  FolderKanban,
  Wrench,
  Users,
  BarChart3,
  ClipboardList,
  LayoutDashboard,
} from 'lucide-react';

const navigation = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/projects', label: 'Proyectos', icon: FolderKanban },
  { to: '/accessories', label: 'Accesorios', icon: Wrench },
  { to: '/reports', label: 'Semáforo', icon: BarChart3 },
  { to: '/users', label: 'Usuarios', icon: Users, adminOnly: true },
  { to: '/audit', label: 'Auditoría', icon: ClipboardList, adminOnly: true },
];

export default function Layout() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const visibleNav = navigation.filter(
    (n) => !n.adminOnly || user?.role === 'ADMIN',
  );

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-slate-900 text-white transition-all duration-300 flex flex-col`}
      >
        <div className="p-4 flex flex-col items-center border-b border-slate-700 relative">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 hover:bg-slate-800 rounded absolute top-3 right-3"
          >
            <Menu size={20} />
          </button>
          {sidebarOpen && <div className="flex flex-col items-center gap-1 w-full mt-4"><h1 className="text-xl font-bold">OBRAS</h1><img src="/logo.png" alt="Logo" className="h-20 w-20 object-contain" /></div>}
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {visibleNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `w-full flex items-center gap-3 px-4 py-2 rounded-lg transition ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-slate-800'
                }`
              }
            >
              <item.icon size={20} />
              {sidebarOpen && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-slate-700 p-4">
          <div className="flex items-center gap-3 px-4 py-2 text-gray-400 text-sm mb-2">
            {sidebarOpen && (
              <span className="truncate">{user?.full_name ?? user?.email}</span>
            )}
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2 text-gray-300 hover:bg-slate-800 rounded-lg transition"
          >
            <LogOut size={20} />
            {sidebarOpen && <span>Cerrar sesión</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
