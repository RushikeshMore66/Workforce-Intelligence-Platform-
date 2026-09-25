'use client';

import React, { useEffect, useState } from 'react';
import {
  CreateUserPayload,
  UserRole,
  WorkerStatus,
} from '@/types';
import { createUser } from '@/lib/api/users';
import { getTeams } from '@/lib/api/teams';
import { getSupervisors } from '@/lib/api/supervisors';
import { ApiRequestError } from '@/lib/api/client';
import { apiClient } from '@/lib/api/client';
import type { TeamViewModel, Supervisor, TeamLeader } from '@/types';

interface CreateUserModalProps {
  onClose: () => void;
  onCreated: () => void;
}

const ROLES: { value: UserRole; label: string }[] = [
  { value: 'WORKER', label: 'Worker' },
  { value: 'TEAM_LEADER', label: 'Team Leader' },
  { value: 'SUPERVISOR', label: 'Supervisor' },
];

const WORKER_STATUSES: { value: WorkerStatus; label: string }[] = [
  { value: 'ACTIVE', label: 'Active' },
  { value: 'ON_LEAVE', label: 'On Leave' },
  { value: 'UNAVAILABLE', label: 'Unavailable' },
];

export function CreateUserModal({ onClose, onCreated }: CreateUserModalProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [company, setCompany] = useState('');
  const [role, setRole] = useState<UserRole>('WORKER');

  const [jobTitle, setJobTitle] = useState('');
  const [teamId, setTeamId] = useState('');
  const [teamLeaderId, setTeamLeaderId] = useState('');
  const [supervisorId, setSupervisorId] = useState('');
  const [workerStatus, setWorkerStatus] = useState<WorkerStatus>('ACTIVE');

  const [tlTeamId, setTlTeamId] = useState('');

  const [teams, setTeams] = useState<TeamViewModel[]>([]);
  const [supervisors, setSupervisors] = useState<Supervisor[]>([]);
  const [teamLeaders, setTeamLeaders] = useState<TeamLeader[]>([]);
  const [loadingRefs, setLoadingRefs] = useState(true);

  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function loadRefs() {
      try {
        const [teamsData, supervisorsData] = await Promise.all([
          getTeams(),
          getSupervisors(),
        ]);
        if (cancelled) return;
        setTeams(teamsData);
        setSupervisors(supervisorsData);

        const usersResp = await apiClient.get<Array<{
          id: string;
          name: string;
          email: string;
          role: string;
          teamLeaderProfileId: string | null;
        }>>('/users');
        if (cancelled) return;

        const tlUsers = usersResp.filter((u) => u.role === 'TEAM_LEADER');
        const tlList: TeamLeader[] = tlUsers.flatMap((u) => {
          if (!u.teamLeaderProfileId) return [];
          const teamForTl = teamsData.find(
            (t) => t.teamLeaderId === u.teamLeaderProfileId,
          );
          return [{
            id: u.teamLeaderProfileId,
            userId: u.id,
            name: u.name,
            email: u.email,
            avatarInitials: '',
            teamId: teamForTl?.id ?? null,
          }];
        });
        setTeamLeaders(tlList);
      } catch {
        // non-fatal
      } finally {
        if (!cancelled) setLoadingRefs(false);
      }
    }
    loadRefs();
    return () => { cancelled = true; };
  }, []);

  const filteredTeamLeaders = teamId
    ? teamLeaders.filter((tl) => tl.teamId === teamId)
    : teamLeaders;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim()) { setError('Name is required.'); return; }
    if (!email.trim()) { setError('Email is required.'); return; }
    if (password.length < 8) { setError('Password must be at least 8 characters.'); return; }
    if (role === 'WORKER' && !jobTitle.trim()) {
      setError('Job title is required for worker accounts.');
      return;
    }

    const payload: CreateUserPayload = {
      email: email.trim(),
      name: name.trim(),
      password,
      role,
      company: company.trim() || undefined,
    };

    if (role === 'WORKER') {
      payload.workerProfile = {
        jobTitle: jobTitle.trim(),
        teamId: teamId || undefined,
        teamLeaderId: teamLeaderId || undefined,
        supervisorId: supervisorId || undefined,
        status: workerStatus,
      };
    } else if (role === 'TEAM_LEADER') {
      payload.teamLeaderProfile = {
        teamId: tlTeamId || undefined,
      };
    } else if (role === 'SUPERVISOR') {
      payload.supervisorProfile = {};
    }

    setIsSaving(true);
    try {
      await createUser(payload);
      setSuccess(true);
      setTimeout(() => { onCreated(); onClose(); }, 800);
    } catch (err: unknown) {
      if (err instanceof ApiRequestError) {
        if (err.status === 409) {
          setError(`A user with email "${email.trim()}" already exists.`);
        } else if (err.status === 403) {
          setError('You are not permitted to create users with this role.');
        } else if (err.status === 400) {
          setError(err.message || 'Invalid organizational relationship.');
        } else if (err.status === 422) {
          setError(err.message || 'Validation failed. Check all required fields.');
        } else {
          setError('Server error. Please try again.');
        }
      } else {
        setError('Unexpected error. Please try again.');
      }
    } finally {
      setIsSaving(false);
    }
  };

  const inputClass =
    'w-full border border-[#D0D5DD] rounded-lg px-3.5 py-2.5 text-sm text-[#172033] placeholder-[#98A2B3] focus:outline-none focus:ring-2 focus:ring-[#263B80]/30 focus:border-[#263B80] transition disabled:opacity-50 disabled:bg-[#F9FAFB]';
  const labelClass = 'block text-sm font-medium text-[#344054] mb-1.5';
  const selectClass =
    'w-full border border-[#D0D5DD] rounded-lg px-3.5 py-2.5 text-sm text-[#172033] focus:outline-none focus:ring-2 focus:ring-[#263B80]/30 focus:border-[#263B80] transition bg-white disabled:opacity-50 disabled:bg-[#F9FAFB]';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 overflow-hidden max-h-[90vh] flex flex-col">
        <div className="px-6 py-5 border-b border-[#E7E8EC] flex-shrink-0">
          <h2 className="text-base font-semibold text-[#172033]">Create User</h2>
          <p className="text-sm text-[#667085] mt-0.5">
            Provision a new account. The user can log in immediately after creation.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4 overflow-y-auto flex-1">
          <div>
            <label className={labelClass} htmlFor="cu-name">
              Full Name <span className="text-red-500">*</span>
            </label>
            <input id="cu-name" type="text" value={name} onChange={(e) => setName(e.target.value)} className={inputClass} placeholder="Jane Smith" required />
          </div>

          <div>
            <label className={labelClass} htmlFor="cu-email">
              Email Address <span className="text-red-500">*</span>
            </label>
            <input id="cu-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} className={inputClass} placeholder="jane@company.com" required autoComplete="off" />
          </div>

          <div>
            <label className={labelClass} htmlFor="cu-password">
              Temporary Password <span className="text-red-500">*</span>
            </label>
            <input id="cu-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} className={inputClass} placeholder="At least 8 characters" required autoComplete="new-password" />
            <p className="text-xs text-[#667085] mt-1">The user should change this after first login.</p>
          </div>

          <div>
            <label className={labelClass} htmlFor="cu-company">Company / Organisation</label>
            <input id="cu-company" type="text" value={company} onChange={(e) => setCompany(e.target.value)} className={inputClass} placeholder="Acme Corp (optional)" />
          </div>

          <div>
            <label className={labelClass} htmlFor="cu-role">
              Role <span className="text-red-500">*</span>
            </label>
            <select id="cu-role" value={role} onChange={(e) => { setRole(e.target.value as UserRole); setTeamId(''); setTeamLeaderId(''); setSupervisorId(''); setTlTeamId(''); setJobTitle(''); }} className={selectClass} required>
              {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
            <p className="text-xs text-[#667085] mt-1">OWNER accounts are bootstrapped via seed script only.</p>
          </div>

          {role === 'WORKER' && (
            <fieldset className="border border-[#E7E8EC] rounded-xl p-4 space-y-4">
              <legend className="px-1 text-xs font-semibold text-[#667085] uppercase tracking-wider">Worker Profile</legend>

              <div>
                <label className={labelClass} htmlFor="cu-job-title">Job Title <span className="text-red-500">*</span></label>
                <input id="cu-job-title" type="text" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} className={inputClass} placeholder="e.g. Backend Engineer" required />
              </div>

              <div>
                <label className={labelClass} htmlFor="cu-team">Team</label>
                <select id="cu-team" value={teamId} onChange={(e) => { setTeamId(e.target.value); setTeamLeaderId(''); }} className={selectClass} disabled={loadingRefs}>
                  <option value="">— No team —</option>
                  {teams.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </div>

              <div>
                <label className={labelClass} htmlFor="cu-tl">Team Leader</label>
                <select id="cu-tl" value={teamLeaderId} onChange={(e) => setTeamLeaderId(e.target.value)} className={selectClass} disabled={loadingRefs}>
                  <option value="">— No team leader —</option>
                  {filteredTeamLeaders.map((tl) => <option key={tl.id} value={tl.id}>{tl.name}</option>)}
                </select>
                {teamId && filteredTeamLeaders.length === 0 && !loadingRefs && (
                  <p className="text-xs text-[#667085] mt-1">No team leaders assigned to this team yet.</p>
                )}
              </div>

              <div>
                <label className={labelClass} htmlFor="cu-supervisor">Supervisor</label>
                <select id="cu-supervisor" value={supervisorId} onChange={(e) => setSupervisorId(e.target.value)} className={selectClass} disabled={loadingRefs}>
                  <option value="">— No supervisor —</option>
                  {supervisors.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>

              <div>
                <label className={labelClass} htmlFor="cu-status">Operational Status</label>
                <select id="cu-status" value={workerStatus} onChange={(e) => setWorkerStatus(e.target.value as WorkerStatus)} className={selectClass}>
                  {WORKER_STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
              </div>
            </fieldset>
          )}

          {role === 'TEAM_LEADER' && (
            <fieldset className="border border-[#E7E8EC] rounded-xl p-4 space-y-4">
              <legend className="px-1 text-xs font-semibold text-[#667085] uppercase tracking-wider">Team Leader Profile</legend>
              <div>
                <label className={labelClass} htmlFor="cu-tl-team">Assigned Team</label>
                <select id="cu-tl-team" value={tlTeamId} onChange={(e) => setTlTeamId(e.target.value)} className={selectClass} disabled={loadingRefs}>
                  <option value="">— No team yet —</option>
                  {teams.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
                <p className="text-xs text-[#667085] mt-1">A team leader can lead at most one team. Leave blank to assign later.</p>
              </div>
            </fieldset>
          )}

          {role === 'SUPERVISOR' && (
            <p className="text-sm text-[#667085] bg-[#F9FAFB] border border-[#E7E8EC] rounded-lg px-4 py-3">
              Supervisor accounts are provisioned with basic identity only. You can assign teams and projects after creation.
            </p>
          )}

          {error && (
            <div className="text-sm text-[#B42318] bg-[#FEF3F2] border border-[#FECDCA] rounded-lg px-3.5 py-2.5">{error}</div>
          )}

          {success && (
            <div className="text-sm text-[#027A48] bg-[#F6FEF9] border border-[#A6F4C5] rounded-lg px-3.5 py-2.5">
              ✓ User created successfully.
            </div>
          )}

          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose} className="flex-1 border border-[#D0D5DD] rounded-lg py-2.5 text-sm font-medium text-[#344054] hover:bg-[#F9FAFB] transition">Cancel</button>
            <button type="submit" disabled={isSaving || success} className="flex-1 bg-[#263B80] hover:bg-[#1a2a5e] disabled:opacity-50 text-white rounded-lg py-2.5 text-sm font-medium transition" id="create-user-submit-btn">
              {isSaving ? 'Creating…' : 'Create User'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
