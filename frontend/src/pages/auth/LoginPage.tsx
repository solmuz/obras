import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useLogin } from '@/hooks/useAuth';
import { LoginRequest } from '@/types';

export default function LoginPage() {
  const navigate = useNavigate();
  const { setTokens, setUser, setError: setStoreError } = useAuthStore();
  const loginMutation = useLogin();
  
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('ChangeMe123!');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const credentials: LoginRequest = { email, password };
      const response = await loginMutation.mutateAsync(credentials);

      // Store tokens
      setTokens(response.access_token, response.refresh_token);
      
      // Navigate to dashboard
      navigate('/dashboard');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Login failed';
      setError(errorMessage);
      setStoreError(errorMessage);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-slate-900">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 text-center">OBRAS</h1>
          <p className="text-gray-600 text-center mb-8">
            Gestión de Accesorios de Izaje
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            <div>
              <label className="block text-gray-700 font-medium mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="admin@example.com"
                required
              />
            </div>

            <div>
              <label className="block text-gray-700 font-medium mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your password"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loginMutation.isPending}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition disabled:opacity-50"
            >
              {loginMutation.isPending ? 'Logging in...' : 'Login'}
            </button>
          </form>

          <p className="text-gray-600 text-sm text-center mt-6">
            Demo credentials enabled for testing
          </p>
        </div>
      </div>
    </div>
  );
}
