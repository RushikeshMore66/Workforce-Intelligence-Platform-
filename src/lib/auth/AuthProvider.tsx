'use client';

import React, { createContext, useState, useEffect, useCallback } from 'react';
import { AuthContextType } from './types';
import { User, LoginCredentials, UpdateProfilePayload, ChangePasswordPayload } from '@/types';
import * as authApi from '@/lib/api/auth';
import { setUnauthorizedCallback } from '@/lib/api/client';

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshUser = useCallback(async () => {
    try {
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refreshUser();
  }, [refreshUser]);

  useEffect(() => {
    // Register global 401 handler — clears user state on token expiry/deactivation
    setUnauthorizedCallback(() => {
      authApi.logout();
      setUser(null);
    });
  }, []);

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    try {
      const loggedInUser = await authApi.login(credentials);
      setUser(loggedInUser);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await authApi.logout();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const updateProfile = async (data: UpdateProfilePayload) => {
    const updatedUser = await authApi.updateProfile(data);
    setUser(updatedUser);
  };

  const changePassword = async (data: ChangePasswordPayload) => {
    await authApi.changePassword(data);
    // No user state change required — password change doesn't affect user claims
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    refreshUser,
    updateProfile,
    changePassword,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
