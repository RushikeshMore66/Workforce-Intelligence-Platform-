'use client';
import { useState, useMemo } from 'react';
import Link from 'next/link';
import { useWorkforce } from './useWorkforce';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, TableEmpty } from '@/components/ui/table';
import { SkeletonTable } from '@/components/ui/skeleton';
import { Search, AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function WorkforcePage() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const { workers, isLoading, error, refetch } = useWorkforce({
    search: search || undefined,
    status: statusFilter || undefined,
  });

  const statusCounts = useMemo(() => {
    if (!workers) return { active: 0, leave: 0, unavailable: 0 };
    return {
      active: workers.filter(w => w.status === 'ACTIVE').length,
      leave: workers.filter(w => w.status === 'ON_LEAVE').length,
      unavailable: workers.filter(w => w.status === 'UNAVAILABLE').length,
    };
  }, [workers]);

  return (
    <div className="max-w-[1400px] mx-auto space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="wi-page-title">Workforce Directory</h1>
          <p className="text-sm text-[#667085] mt-0.5">View and manage workers across the organization.</p>
        </div>
        {!isLoading && !error && workers.length > 0 && (
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
        )}
      </div>

      {/* Filters */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl px-4 py-3.5 flex flex-wrap gap-3 items-center shadow-[0_1px_3px_0_rgba(16,24,40,0.06)]">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#9CA3AF]" />
          <Input 
            value={search} 
            onChange={e => setSearch(e.target.value)} 
            placeholder="Search by name or role..." 
            className="pl-9" 
          />
        </div>
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
        {!isLoading && !error && (
          <span className="text-xs text-[#9CA3AF]">{workers.length} workers</span>
        )}
      </div>

      {isLoading ? (
        <SkeletonTable rows={8} cols={4} />
      ) : error ? (
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-12 text-center shadow-sm">
          <AlertTriangle className="w-8 h-8 text-[#F04438] mx-auto mb-3" />
          <h3 className="text-base font-semibold text-[#172033]">Failed to load workforce</h3>
          <p className="text-sm text-[#667085] mt-1 mb-4">There was a problem communicating with the server.</p>
          <Button variant="outline" onClick={refetch}>
            <RefreshCw className="w-4 h-4 mr-2" /> Retry
          </Button>
        </div>
      ) : (
        <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Worker</TableHead>
                <TableHead className="hidden md:table-cell">Role</TableHead>
                <TableHead className="hidden sm:table-cell">Team ID</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {workers.length === 0 ? (
                <TableEmpty colSpan={4} message="No workers match your filters." />
              ) : (
                workers.map(w => (
                  <TableRow key={w.id}>
                    <TableCell>
                      <Link href={`/workforce/${w.id}`} className="flex items-center gap-2.5 group">
                        <Avatar initials={w.avatarInitials} name={w.name} size="sm" />
                        <span className="font-medium text-[#172033] group-hover:text-[#263B80] transition-colors">{w.name}</span>
                      </Link>
                    </TableCell>
                    <TableCell className="hidden md:table-cell text-[#667085] text-xs">{w.role}</TableCell>
                    <TableCell className="hidden sm:table-cell text-[#667085] text-xs font-mono">{w.teamId ?? '—'}</TableCell>
                    <TableCell>
                      <Badge
                        variant={w.status === 'ACTIVE' ? 'success' : w.status === 'ON_LEAVE' ? 'warning' : 'default'}
                        dot
                      >
                        {w.status === 'ACTIVE' ? 'Active' : w.status === 'ON_LEAVE' ? 'On Leave' : 'Unavailable'}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
