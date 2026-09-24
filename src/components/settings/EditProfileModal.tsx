'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth/useAuth';

interface EditProfileModalProps {
  onClose: () => void;
}

export function EditProfileModal({ onClose }: EditProfileModalProps) {
  const { user, updateProfile } = useAuth();
  const [name, setName] = useState(user?.name ?? '');
  const [company, setCompany] = useState(user?.company ?? '');
  const [error, setError] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!name.trim()) {
      setError('Name is required.');
      return;
    }
    setIsSaving(true);
    try {
      await updateProfile({
        name: name.trim(),
        company: company.trim() || undefined,
      });
      setSuccess(true);
      setTimeout(onClose, 800);
    } catch {
      setError('Failed to update profile. Please try again.');
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
          <h2 className="text-base font-semibold text-[#172033]">Edit Profile</h2>
          <p className="text-sm text-[#667085] mt-0.5">Update your name and company.</p>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          <div>
            <label className="block text-sm font-medium text-[#344054] mb-1.5" htmlFor="edit-name">
              Full Name <span className="text-red-500">*</span>
            </label>
            <input
              id="edit-name"
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full border border-[#D0D5DD] rounded-lg px-3.5 py-2.5 text-sm text-[#172033] placeholder-[#98A2B3] focus:outline-none focus:ring-2 focus:ring-[#263B80]/30 focus:border-[#263B80] transition"
              placeholder="Your full name"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#344054] mb-1.5" htmlFor="edit-company">
              Company
            </label>
            <input
              id="edit-company"
              type="text"
              value={company}
              onChange={e => setCompany(e.target.value)}
              className="w-full border border-[#D0D5DD] rounded-lg px-3.5 py-2.5 text-sm text-[#172033] placeholder-[#98A2B3] focus:outline-none focus:ring-2 focus:ring-[#263B80]/30 focus:border-[#263B80] transition"
              placeholder="Your company or organisation"
            />
          </div>

          {error && (
            <div className="text-sm text-[#B42318] bg-[#FEF3F2] border border-[#FECDCA] rounded-lg px-3.5 py-2.5">
              {error}
            </div>
          )}

          {success && (
            <div className="text-sm text-[#027A48] bg-[#F6FEF9] border border-[#A6F4C5] rounded-lg px-3.5 py-2.5">
              ✓ Profile updated successfully.
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
              id="save-profile-btn"
            >
              {isSaving ? 'Saving…' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
