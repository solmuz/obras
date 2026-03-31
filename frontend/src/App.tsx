import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/store/authStore';
import ProtectedRoute from '@/routes/ProtectedRoute';
import Layout from '@/components/Layout';
import LoginPage from '@/pages/auth/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import ProjectsPage from '@/pages/ProjectsPage';
import ProjectDetailPage from '@/pages/ProjectDetailPage';
import AccessoriesPage from '@/pages/AccessoriesPage';
import AccessoryDetailPage from '@/pages/AccessoryDetailPage';
import UsersPage from '@/pages/UsersPage';
import ReportsPage from '@/pages/ReportsPage';
import AuditPage from '@/pages/AuditPage';

const queryClient = new QueryClient();

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
            <Route path="/accessories" element={<AccessoriesPage />} />
            <Route path="/accessories/:accessoryId" element={<AccessoryDetailPage />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/audit" element={<AuditPage />} />
          </Route>
          <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/login" />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
