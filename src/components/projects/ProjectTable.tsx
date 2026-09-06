'use client';
import { useState, useMemo } from 'react';
import Link from 'next/link';
import { Project, Supervisor } from '@/types';
import { Progress } from '@/components/ui/progress';
import { ProjectHealthBadge } from './ProjectHealthBadge';
import { ProjectStatusBadge } from './ProjectStatusBadge';
import { ProjectPriorityBadge } from './ProjectPriorityBadge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, TableEmpty } from '@/components/ui/table';
import { formatDate, daysUntil } from '@/lib/utils';
import { ArrowUpDown } from 'lucide-react';

interface Props {
  projects: Project[];
  supervisors: Supervisor[];
  search?: string;
  statusFilter?: string;
  healthFilter?: string;
  priorityFilter?: string;
}

type SortKey = 'name' | 'progress' | 'deadline' | 'priority';
type SortDir = 'asc' | 'desc';

const PRIORITY_ORDER = { LOW: 0, MEDIUM: 1, HIGH: 2, CRITICAL: 3 };

function SortableHead({ k, label, className, toggleSort }: { k: SortKey; label: string; className?: string, toggleSort: (key: SortKey) => void }) {
  return (
    <TableHead
      className={`cursor-pointer select-none hover:text-[#172033] ${className ?? ''}`}
      onClick={() => toggleSort(k)}
    >
      <span className="inline-flex items-center gap-1">
        {label}
        <ArrowUpDown className="w-3 h-3 opacity-50" />
      </span>
    </TableHead>
  );
}

export function ProjectTable({ projects, supervisors, search, statusFilter, healthFilter, priorityFilter }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>('deadline');
  const [sortDir, setSortDir] = useState<SortDir>('asc');

  const supMap = useMemo(
    () => Object.fromEntries(supervisors.map(s => [s.id, s])),
    [supervisors]
  );

  const filtered = useMemo(() => {
    let list = [...projects];
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.client.toLowerCase().includes(q)
      );
    }
    if (statusFilter) list = list.filter(p => p.status === statusFilter);
    if (healthFilter) list = list.filter(p => p.health === healthFilter);
    if (priorityFilter) list = list.filter(p => p.priority === priorityFilter);
    return list.sort((a, b) => {
      let cmp = 0;
      switch (sortKey) {
        case 'name':     cmp = a.name.localeCompare(b.name); break;
        case 'progress': cmp = a.progress - b.progress; break;
        case 'deadline': cmp = a.deadline.localeCompare(b.deadline); break;
        case 'priority': cmp = PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority]; break;
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [projects, search, statusFilter, healthFilter, priorityFilter, sortKey, sortDir]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortKey(key); setSortDir('asc'); }
  }

  return (
    <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-[0_1px_3px_0_rgba(16,24,40,0.06)] overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <SortableHead k="name" label="Project" toggleSort={toggleSort} />
            <TableHead className="hidden md:table-cell">Client</TableHead>
            <TableHead className="hidden lg:table-cell">Supervisor</TableHead>
            <SortableHead k="progress" label="Progress" className="hidden sm:table-cell" toggleSort={toggleSort} />
            <SortableHead k="deadline" label="Deadline" toggleSort={toggleSort} />
            <SortableHead k="priority" label="Priority" className="hidden md:table-cell" toggleSort={toggleSort} />
            <TableHead>Health</TableHead>
            <TableHead className="hidden sm:table-cell">Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filtered.length === 0 ? (
            <TableEmpty colSpan={8} message="No projects match your filters." />
          ) : (
            filtered.map(proj => {
              const sup = proj.supervisorId ? supMap[proj.supervisorId] : undefined;
              const days = daysUntil(proj.deadline);
              return (
                <TableRow key={proj.id}>
                  <TableCell>
                    <Link href={`/projects/${proj.id}`} className="font-medium text-[#172033] hover:text-[#263B80] transition-colors">
                      {proj.name}
                    </Link>
                  </TableCell>
                  <TableCell className="hidden md:table-cell text-[#667085]">{proj.client}</TableCell>
                  <TableCell className="hidden lg:table-cell text-[#667085]">{sup?.name ?? '—'}</TableCell>
                  <TableCell className="hidden sm:table-cell">
                    <div className="flex items-center gap-2 min-w-[100px]">
                      <Progress value={proj.progress} className="flex-1" />
                      <span className="text-xs text-[#667085] w-7 text-right">{proj.progress}%</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <div className="text-sm text-[#172033]">{formatDate(proj.deadline)}</div>
                      <div className={`text-xs mt-0.5 ${days < 30 ? 'text-[#B54708]' : 'text-[#9CA3AF]'}`}>
                        {days > 0 ? `${days}d left` : 'Overdue'}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="hidden md:table-cell">
                    <ProjectPriorityBadge priority={proj.priority} />
                  </TableCell>
                  <TableCell>
                    <ProjectHealthBadge health={proj.health} />
                  </TableCell>
                  <TableCell className="hidden sm:table-cell">
                    <ProjectStatusBadge status={proj.status} />
                  </TableCell>
                </TableRow>
              );
            })
          )}
        </TableBody>
      </Table>
    </div>
  );
}
