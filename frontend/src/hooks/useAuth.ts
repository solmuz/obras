import { useMutation, useQueryClient } from '@tanstack/react-query';
import { authApi } from '@/services/authApi';
import { useAuthStore } from '@/store/authStore';
import { LoginRequest } from '@/types';

export const useLogin = () => {
  const { setTokens, setUser, setError, setLoading } = useAuthStore();

  return useMutation({
    mutationFn: async (credentials: LoginRequest) => {
      return await authApi.login(credentials);
    },
    onMutate: () => {
      setLoading(true);
      setError(null);
    },
    onSuccess: async (data) => {
      // Store tokens right away
      setTokens(data.access_token, data.refresh_token);

      // Try to fetch and store user profile
      try {
        const user = await authApi.getProfile();
        setUser(user);
      } catch (err) {
        console.warn('Could not fetch user profile:', err);
        // Still consider login successful, profile will load on next request
      }
    },
    onError: (error: any) => {
      const errorMessage =
        error?.response?.data?.detail ||
        error?.message ||
        'Login failed. Please check your credentials.';
      setError(errorMessage);
    },
    onSettled: () => {
      setLoading(false);
    },
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  const { logout } = useAuthStore();

  return useMutation({
    mutationFn: async () => {
      try {
        await authApi.logout();
      } catch (err) {
        console.warn('Logout API call failed, clearing local state anyway:', err);
      }
    },
    onSuccess: () => {
      logout();
      queryClient.clear();
    },
  });
};

export const useRefreshToken = () => {
  const { setTokens, setError } = useAuthStore();

  return useMutation({
    mutationFn: async (refreshToken: string) => {
      return await authApi.refresh(refreshToken);
    },
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
      setError(null);
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 'Token refresh failed';
      setError(errorMessage);
    },
  });
};
