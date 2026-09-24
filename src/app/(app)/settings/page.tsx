'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth/useAuth';
import { ProfileCard } from '@/components/settings/ProfileCard';
import { EditProfileModal } from '@/components/settings/EditProfileModal';
import { ChangePasswordModal } from '@/components/settings/ChangePasswordModal';

export default function SettingsPage() {
  const { user } = useAuth();
  const [showEditProfile, setShowEditProfile] = useState(false);
  const [showChangePassword, setShowChangePassword] = useState(false);

  return (
    <div className="max-w-[700px] mx-auto space-y-6">
      <div>
        <h1 className="wi-page-title">Settings</h1>
        <p className="text-sm text-[#667085] mt-0.5">
          Manage your account preferences and application settings.
        </p>
      </div>

      {/* Profile Card */}
      <ProfileCard />

      {/* Account section */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-[#E7E8EC] flex items-center justify-between">
          <h2 className="text-sm font-semibold text-[#172033]">Account</h2>
          <button
            onClick={() => setShowEditProfile(true)}
            className="text-xs font-medium text-[#263B80] hover:text-[#1a2a5e] transition-colors px-3 py-1.5 rounded-lg border border-[#E7E8EC] hover:border-[#263B80] hover:bg-[#F5F7FF]"
            id="edit-profile-btn"
          >
            Edit Profile
          </button>
        </div>
        <div className="divide-y divide-[#F3F4F6]">
          <div className="flex items-center justify-between px-5 py-4">
            <div className="text-sm font-medium text-[#172033]">Full Name</div>
            <span className="text-sm text-[#172033]">{user?.name || '—'}</span>
          </div>
          <div className="flex items-center justify-between px-5 py-4">
            <div className="text-sm font-medium text-[#172033]">Email Address</div>
            <span className="text-sm text-[#9CA3AF]">{user?.email || '—'}</span>
          </div>
          <div className="flex items-center justify-between px-5 py-4">
            <div className="text-sm font-medium text-[#172033]">Company</div>
            <span className="text-sm text-[#172033]">{user?.company || '—'}</span>
          </div>
          <div className="flex items-center justify-between px-5 py-4">
            <div className="text-sm font-medium text-[#172033]">Role</div>
            <span className="text-sm text-[#9CA3AF]">{user?.role || '—'}</span>
          </div>
        </div>
      </div>

      {/* Security */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-[#E7E8EC]">
          <h2 className="text-sm font-semibold text-[#172033]">Security</h2>
        </div>
        <div className="px-5 py-4 flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-[#172033]">Password</div>
            <div className="text-xs text-[#667085] mt-0.5">
              Use a strong password with at least 8 characters.
            </div>
          </div>
          <button
            onClick={() => setShowChangePassword(true)}
            className="text-xs font-medium text-[#263B80] hover:text-[#1a2a5e] transition-colors px-3 py-1.5 rounded-lg border border-[#E7E8EC] hover:border-[#263B80] hover:bg-[#F5F7FF]"
            id="change-password-btn"
          >
            Change Password
          </button>
        </div>
      </div>

      {/* Notifications */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-[#E7E8EC]">
          <h2 className="text-sm font-semibold text-[#172033]">Notifications</h2>
        </div>
        <div className="divide-y divide-[#F3F4F6]">
          {[
            { label: 'Blocker alerts', on: true },
            { label: 'Deadline reminders', on: true },
            { label: 'Project updates', on: true },
            { label: 'Weekly digest email', on: false },
          ].map(item => (
            <div key={item.label} className="flex items-center justify-between px-5 py-4">
              <div className="text-sm font-medium text-[#172033]">{item.label}</div>
              <div
                className={`relative inline-flex w-9 h-5 rounded-full transition-colors ${
                  item.on ? 'bg-[#263B80]' : 'bg-[#D1D5DB]'
                }`}
              >
                <span
                  className={`inline-block w-4 h-4 rounded-full bg-white shadow transition-transform mt-0.5 ${
                    item.on ? 'translate-x-4' : 'translate-x-0.5'
                  }`}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Display */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-[#E7E8EC]">
          <h2 className="text-sm font-semibold text-[#172033]">Display</h2>
        </div>
        <div className="divide-y divide-[#F3F4F6]">
          {[
            { label: 'Date format', value: 'DD MMM YYYY' },
            { label: 'Time zone', value: 'Asia/Kolkata (IST, UTC+5:30)' },
            { label: 'Currency', value: 'INR (₹)' },
          ].map(item => (
            <div key={item.label} className="flex items-center justify-between px-5 py-4">
              <div className="text-sm font-medium text-[#172033]">{item.label}</div>
              <span className="text-sm text-[#9CA3AF]">{item.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Account Actions */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-[#172033] mb-3">Account Actions</h2>
        <div className="border border-[#FECDCA] rounded-lg p-4 bg-[#FEF3F2]">
          <p className="text-sm text-[#B42318] font-medium">Account deletion and data export</p>
          <p className="text-sm text-[#B42318] mt-1">
            Contact your organisation owner to request account changes.
          </p>
        </div>
      </div>

      {/* Modals */}
      {showEditProfile && (
        <EditProfileModal onClose={() => setShowEditProfile(false)} />
      )}
      {showChangePassword && (
        <ChangePasswordModal onClose={() => setShowChangePassword(false)} />
      )}
    </div>
  );
}
