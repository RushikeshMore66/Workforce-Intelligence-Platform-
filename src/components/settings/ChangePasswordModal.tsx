'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth/useAuth';

interface ChangePasswordModalProps {
  onClose: () => void;
}

export function ChangePasswordModal({ onClose }: ChangePasswordModalProps) {
  const { changePassword } = useAuth();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (newPassword.length < 8) {
      setError('New password must be at least 8 characters.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('New passwords do not match.');
      return;
    }
    if (newPassword === currentPassword) {
      setError('New password must be different from your current password.');
      return;
    }

    setIsSaving(true);
    try {
      await changePassword({ currentPassword, newPassword });
      setSuccess(true);
      setTimeout(onClose, 1200);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : '';
      if (msg.includes('400') || msg.toLowerCase().includes('incorrect')) {
        setError('Current password is incorrect.');
      } else {
        setError('Failed to change password. Please try again.');
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 overflow-hidden">
        <div className="px-6 py-5 border-b border-[#E7E8EC]">
          <h2 className="text-base font-semibold text-[#172033]">Change Password</h2>
          <p className="text-sm text-[#667085] mt-0.5">
            Your current password is required to confirm this change.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          <div>
            <label
              className="block text-sm font-medium text-[#344054] mb-1.5"
              htmlFor="current-password"
            >
              Current Password
            </label>
            <input
              id="current-password"
              type="password"
              value={currentPassword}
              onChange={e => setCurrentPassword(e.target.value)}
              className="w-full border border-[#D0D5DD] rounded-lg px-3.5 py-2.5 text-sm text-[#172033] placeholder-[#98A2B3] focus:outline-none focus:ring-2 focus:ring-[#263B80]/30 focus:border-[#263B80] transition"
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
          </div>

          <div>
            <label
              className="block text-sm font-medium text-[#344054] mb-1.5"
              htmlFor="new-password"
            >
              New Password
            </label>
            <input
              id="new-password"
              type="password"
              value={newPassword}
              onChange={e => setNewPassword(e.target.value)}
              className="w-full border border-[#D0D5DD] rounded-lg px-3.5 py-2.5 text-sm text-[#172033] placeholder-[#98A2B3] focus:outline-none focus:ring-2 focus:ring-[#263B80]/30 focus:border-[#263B80] transition"
              placeholder="At least 8 characters"
              required
              autoComplete="new-password"
            />
          </div>

          <div>
            <label
              className="block text-sm font-medium text-[#344054] mb-1.5"
              htmlFor="confirm-password"
            >
              Confirm New Password
            </label>
            <input
              id="confirm-password"
              type="password"
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              className="w-full border border-[#D0D5DD] rounded-lg px-3.5 py-2.5 text-sm text-[#172033] placeholder-[#98A2B3] focus:outline-none focus:ring-2 focus:ring-[#263B80]/30 focus:border-[#263B80] transition"
              placeholder="Repeat new password"
              required
              autoComplete="new-password"
            />
          </div>

          {error && (
            <div className="text-sm text-[#B42318] bg-[#FEF3F2] border border-[#FECDCA] rounded-lg px-3.5 py-2.5">
              {error}
            </div>
          )}

          {success && (
            <div className="text-sm text-[#027A48] bg-[#F6FEF9] border border-[#A6F4C5] rounded-lg px-3.5 py-2.5">
              ✓ Password changed successfully.
            </div>
          )}

          <div className="flex gap-3 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 border border-[#D0D5DD] rounded-lg py-2.5 text-sm font-medium text-[#344054] hover:bg-[#F9FAFB] transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving || success}
              className="flex-1 bg-[#263B80] hover:bg-[#1a2a5e] disabled:opacity-50 text-white rounded-lg py-2.5 text-sm font-medium transition"
              id="save-password-btn"
            >
              {isSaving ? 'Changing…' : 'Change Password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
