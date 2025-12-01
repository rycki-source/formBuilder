import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

export const useAuth = () => {
  const { user, isAuthenticated, isLoading, error, login, logout, fetchUser, clearError } = useAuthStore();

  useEffect(() => {
    // Vérifier si l'utilisateur est connecté au chargement
    if (!isAuthenticated && !isLoading) {
      fetchUser();
    }
  }, []);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    clearError,
  };
};
