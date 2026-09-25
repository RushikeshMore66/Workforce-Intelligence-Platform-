'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { getUsers, activateUser, deactivateUser } from '@/lib/api/users';
import { ManagedUser } from '@/types';
import { useAuth } from '@/lib/auth/useAuth';
import { ApiRequestError } from '@/lib/api/client';
import { CreateUserModal } from '@/components/admin/CreateUserModal';

export default function AdminUsersPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (err: unknown) {
      if (err instanceof ApiRequestError) {
        if (err.status === 401) {
          setError('Your session has expired. Please log in again.');
        } else if (err.status === 403) {
          setError('Access denied. Only Owners can view user management.');
        } else {
          setError('Failed to load users. Please try again.');
        }
      } else {
        setError('Failed to load users. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchUsers();
  }, [fetchUsers]);

  const handleToggleStatus = async (user: ManagedUser) => {
    if (user.id === currentUser?.id) return;

    setActionLoadingId(user.id);
    try {
      if (user.isActive) {
        await deactivateUser(user.id);
      } else {
        await activateUser(user.id);
      }
      await fetchUsers();
    } catch (err: unknown) {
      const msg = err instanceof ApiRequestError ? err.message : 'Failed to change user status.';
      setError(msg || 'Failed to change user status. Please try again.');
    } finally {
      setActionLoadingId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#263B80]"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="wi-page-title">User Management</h1>
          <p className="text-sm text-[#667085] mt-0.5">
            Manage system access and account lifecycle for all users.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-2 bg-[#263B80] hover:bg-[#1a2a5e] text-white text-sm font-medium px-4 py-2.5 rounded-lg transition"
          id="create-user-btn"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create User
        </button>
      </div>

      {error && (
        <div className="text-sm text-[#B42318] bg-[#FEF3F2] border border-[#FECDCA] rounded-lg px-4 py-3">
          {error}
        </div>
      )}

      {/* Users table */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-[#344054]">
            <thead className="bg-[#F9FAFB] border-b border-[#E7E8EC] text-xs font-medium text-[#667085] uppercase tracking-wider">
              <tr>
                <th className="px-6 py-3">User</th>
                <th className="px-6 py-3">Role</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Joined</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F3F4F6]">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-[#F9FAFB] transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#E5E9F4] text-[#263B80] flex items-center justify-center font-semibold text-xs">
                        {u.avatarInitials || u.name.charAt(0)}
                      </div>
                      <div>
                        <div className="font-medium text-[#172033]">{u.name}</div>
                        <div className="text-xs text-[#667085]">{u.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#F3F4F6] text-[#374151]">
                      {u.role.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {u.isActive ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#ECFDF3] text-[#027A48]">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#12B76A]"></span>
                        Active
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#FEF3F2] text-[#B42318]">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#F04438]"></span>
                        Deactivated
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-xs text-[#667085]">
                    {new Date(u.createdAt).toLocaleDateString(undefined, {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right font-medium">
                    {u.id !== currentUser?.id && (
                      <button
                        onClick={() => handleToggleStatus(u)}
                        disabled={actionLoadingId === u.id}
                        className={`text-xs px-3 py-1.5 rounded-lg border transition ${
                          u.isActive
                            ? 'text-[#B42318] border-[#FECDCA] hover:bg-[#FEF3F2] bg-white'
                            : 'text-[#027A48] border-[#A6F4C5] hover:bg-[#F6FEF9] bg-white'
                        } disabled:opacity-50`}
                      >
                        {actionLoadingId === u.id
                          ? 'Updating...'
                          : u.isActive
                          ? 'Deactivate'
                          : 'Activate'}
                      </button>
                    )}
                    {u.id === currentUser?.id && (
                      <span className="text-xs text-[#9CA3AF]">Current User</span>
                    )}
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-sm text-[#667085]">
                    No users found. Use the &quot;Create User&quot; button to provision the first account.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create user modal */}
      {showCreateModal && (
        <CreateUserModal
          onClose={() => setShowCreateModal(false)}
          onCreated={fetchUsers}
        />
      )}
    </div>
  );
}
