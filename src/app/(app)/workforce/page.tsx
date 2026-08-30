'use client';
import { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { getWorkers } from '@/lib/api/workers';
import { getTeams } from '@/lib/api/teams';
import { Worker, Team } from '@/types';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, TableEmpty } from '@/components/ui/table';
import { SkeletonTable } from '@/components/ui/skeleton';
import { Search } from 'lucide-react';

export default function WorkforcePage() {
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [teamFilter, setTeamFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    Promise.all([getWorkers(), getTeams()]).then(([w, t]) => {
      setWorkers(w); setTeams(t); setLoading(false);
    });
  }, []);

  const teamMap = useMemo(() => Object.fromEntries(teams.map(t => [t.id, t])), [teams]);

  const filtered = useMemo(() => {
    return workers.filter(w => {
      const q = search.toLowerCase();
      const matchSearch = !search || w.name.toLowerCase().includes(q) || w.role.toLowerCase().includes(q);
      const matchTeam = !teamFilter || w.teamId === teamFilter;
      const matchStatus = !statusFilter || w.status === statusFilter;
      return matchSearch && matchTeam && matchStatus;
    });
  }, [workers, search, teamFilter, statusFilter]);

  const statusCounts = useMemo(() => ({
    active: workers.filter(w => w.status === 'ACTIVE').length,
    leave: workers.filter(w => w.status === 'ON_LEAVE').length,
    unavailable: workers.filter(w => w.status === 'UNAVAILABLE').length,
  }), [workers]);

  return (
    <div className="max-w-[1400px] mx-auto space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="wi-page-title">Workforce</h1>
          <p className="text-sm text-[#667085] mt-0.5">View and manage all 70 workers across the organization.</p>
        </div>
        <div className="flex flex-wrap gap-3">
          {[
            { label: 'Active', value: statusCounts.active, color: 'text-[#027A48]' },
            { label: 'On Leave', value: statusCounts.leave, color: 'text-[#B54708]' },
            { label: 'Unavailable', value: statusCounts.unavailable, color: 'text-[#667085]' },
          ].map(s => (
            <div key={s.label} className="bg-white border border-[#E7E8EC] rounded-lg px-3 py-2 text-center shadow-sm">
              <div className={`text-lg font-bold ${s.color}`}>{s.value}</div>
              <div className="text-[10px] text-[#9CA3AF]">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl px-4 py-3.5 flex flex-wrap gap-3 items-center shadow-sm">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#9CA3AF]" />
          <Input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by name or role..." className="pl-9" />
        </div>
        <Select value={teamFilter} onValueChange={setTeamFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="All Teams" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Teams</SelectItem>
            {teams.map(t => <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Statuses</SelectItem>
            <SelectItem value="ACTIVE">Active</SelectItem>
            <SelectItem value="ON_LEAVE">On Leave</SelectItem>
            <SelectItem value="UNAVAILABLE">Unavailable</SelectItem>
          </SelectContent>
        </Select>
        <span className="text-xs text-[#9CA3AF]">{filtered.length} workers</span>
      </div>

      {loading ? (
        <SkeletonTable rows={8} cols={6} />
      ) : (
        <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Worker</TableHead>
                <TableHead className="hidden md:table-cell">Role</TableHead>
                <TableHead className="hidden sm:table-cell">Team</TableHead>
                <TableHead className="hidden lg:table-cell">Completed</TableHead>
                <TableHead className="hidden lg:table-cell">In Progress</TableHead>
                <TableHead>Blocked</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.length === 0 ? (
                <TableEmpty colSpan={7} message="No workers match your filters." />
              ) : (
                filtered.map(w => {
                  const team = teamMap[w.teamId];
                  return (
                    <TableRow key={w.id}>
                      <TableCell>
                        <Link href={`/workforce/${w.id}`} className="flex items-center gap-2.5 group">
                          <Avatar initials={w.avatarInitials} name={w.name} size="sm" />
                          <span className="font-medium text-[#172033] group-hover:text-[#263B80] transition-colors">{w.name}</span>
                        </Link>
                      </TableCell>
                      <TableCell className="hidden md:table-cell text-[#667085] text-xs">{w.role}</TableCell>
                      <TableCell className="hidden sm:table-cell text-[#667085] text-xs">{team?.name ?? '—'}</TableCell>
                      <TableCell className="hidden lg:table-cell text-sm text-[#027A48] font-medium">{w.completedTaskCount}</TableCell>
                      <TableCell className="hidden lg:table-cell text-sm text-[#263B80] font-medium">{w.inProgressTaskCount}</TableCell>
                      <TableCell>
                        {w.blockedTaskCount > 0 ? (
                          <Badge variant="danger">{w.blockedTaskCount}</Badge>
                        ) : (
                          <span className="text-xs text-[#9CA3AF]">—</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={w.status === 'ACTIVE' ? 'success' : w.status === 'ON_LEAVE' ? 'warning' : 'default'}
                          dot
                        >
                          {w.status === 'ACTIVE' ? 'Active' : w.status === 'ON_LEAVE' ? 'On Leave' : 'Unavailable'}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
