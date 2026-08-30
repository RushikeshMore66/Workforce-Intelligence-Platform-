/* eslint-disable @typescript-eslint/no-require-imports */
const fs = require('fs');
const path = require('path');

function ensureDirSync(dirpath) {
    if (!fs.existsSync(dirpath)) {
        fs.mkdirSync(dirpath, { recursive: true });
    }
}

// 1. Move dashboard to (app) group
const moveFiles = [
    { src: 'src/app/dashboard/layout.tsx', dest: 'src/app/(app)/layout.tsx' },
    { src: 'src/app/dashboard/page.tsx', dest: 'src/app/(app)/dashboard/page.tsx' },
];

moveFiles.forEach(({ src, dest }) => {
    if (fs.existsSync(src)) {
        ensureDirSync(path.dirname(dest));
        fs.renameSync(src, dest);
    }
});

// Remove old dashboard directory if empty
if (fs.existsSync('src/app/dashboard')) {
    fs.rmSync('src/app/dashboard', { recursive: true, force: true });
}

// 2. Define all new files
const files = {
    'src/types/index.ts': `export type Role = 'OWNER' | 'SUPERVISOR' | 'TEAM_LEADER' | 'WORKER';

export type ProjectStatus = 'PLANNED' | 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'CANCELLED';
export type ProjectHealth = 'ON_TRACK' | 'AT_RISK' | 'DELAYED';
export type ProjectPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface Project {
  id: string;
  name: string;
  client: string;
  description: string;
  startDate: string;
  deadline: string;
  priority: ProjectPriority;
  supervisorId: string;
  
  // Generated/Maintained by system
  status: ProjectStatus;
  health: ProjectHealth;
  progress: number;
  teamCount: number;
  createdAt: string;
}

export interface CreateProjectInput {
  name: string;
  client: string;
  description: string;
  startDate: string;
  deadline: string;
  priority: ProjectPriority;
  supervisorId: string;
}

export interface UpdateProjectInput extends Partial<CreateProjectInput> {
  status?: ProjectStatus;
  health?: ProjectHealth;
  progress?: number;
}

export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'COMPLETED' | 'BLOCKED';

export interface Task {
  id: string;
  projectId: string;
  title: string;
  assigneeId: string;
  teamId: string;
  status: TaskStatus;
  priority: ProjectPriority;
  dueDate: string;
}

export interface Blocker {
  id: string;
  projectId: string;
  title: string;
  description: string;
  ownerId: string;
  createdDate: string;
  status: 'OPEN' | 'RESOLVED';
}

export interface ProjectActivity {
  id: string;
  projectId: string;
  description: string;
  userId: string;
  timestamp: string;
}
`,

    'src/lib/api/mock/projects-repository.ts': `import { Project, CreateProjectInput, UpdateProjectInput } from '@/types';

const STORAGE_KEY = 'wi_mock_projects';

const INITIAL_PROJECTS: Project[] = [
  {
    id: 'proj-1',
    name: 'Hotel Billing System',
    client: 'Grand Hotels Inc',
    description: 'A comprehensive billing and invoicing system.',
    startDate: '2026-01-10',
    deadline: '2026-10-15',
    priority: 'HIGH',
    supervisorId: 'sup-1',
    status: 'ACTIVE',
    health: 'ON_TRACK',
    progress: 76,
    teamCount: 21,
    createdAt: '2026-01-01T00:00:00Z'
  },
  {
    id: 'proj-2',
    name: 'Resort Management Platform',
    client: 'Seaside Resorts',
    description: 'Complete management system for resort operations.',
    startDate: '2026-03-01',
    deadline: '2026-12-01',
    priority: 'MEDIUM',
    supervisorId: 'sup-2',
    status: 'ACTIVE',
    health: 'ON_TRACK',
    progress: 45,
    teamCount: 15,
    createdAt: '2026-02-15T00:00:00Z'
  },
  {
    id: 'proj-3',
    name: 'CRM Development',
    client: 'TechCorp',
    description: 'Internal CRM system.',
    startDate: '2026-05-01',
    deadline: '2026-09-30',
    priority: 'CRITICAL',
    supervisorId: 'sup-3',
    status: 'ACTIVE',
    health: 'DELAYED',
    progress: 30,
    teamCount: 8,
    createdAt: '2026-04-20T00:00:00Z'
  },
  {
    id: 'proj-4',
    name: 'Automation Platform',
    client: 'Logistics Pro',
    description: 'Workflow automation.',
    startDate: '2026-06-01',
    deadline: '2026-11-30',
    priority: 'HIGH',
    supervisorId: 'sup-1',
    status: 'ACTIVE',
    health: 'AT_RISK',
    progress: 15,
    teamCount: 12,
    createdAt: '2026-05-15T00:00:00Z'
  }
];

class ProjectsRepository {
  private getProjects(): Project[] {
    if (typeof window === 'undefined') return INITIAL_PROJECTS;
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_PROJECTS));
      return INITIAL_PROJECTS;
    }
    return JSON.parse(stored);
  }

  private saveProjects(projects: Project[]) {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
    }
  }

  async getAll(): Promise<Project[]> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));
    return this.getProjects();
  }

  async getById(id: string): Promise<Project | null> {
    await new Promise(resolve => setTimeout(resolve, 200));
    const projects = this.getProjects();
    return projects.find(p => p.id === id) || null;
  }

  async create(input: CreateProjectInput): Promise<Project> {
    await new Promise(resolve => setTimeout(resolve, 500));
    const projects = this.getProjects();
    const newProject: Project = {
      ...input,
      id: \`proj-\${Date.now()}\`,
      status: 'PLANNED',
      health: 'ON_TRACK',
      progress: 0,
      teamCount: 0, // Will be updated as teams are assigned
      createdAt: new Date().toISOString()
    };
    this.saveProjects([...projects, newProject]);
    return newProject;
  }

  async update(id: string, input: UpdateProjectInput): Promise<Project | null> {
    await new Promise(resolve => setTimeout(resolve, 400));
    const projects = this.getProjects();
    const idx = projects.findIndex(p => p.id === id);
    if (idx === -1) return null;
    
    const updated = { ...projects[idx], ...input };
    projects[idx] = updated;
    this.saveProjects(projects);
    return updated;
  }
}

export const mockProjectsRepo = new ProjectsRepository();
`,

    'src/lib/api/projects.ts': `import { CreateProjectInput, Project, UpdateProjectInput } from '@/types';
import { mockProjectsRepo } from './mock/projects-repository';

export async function getProjects(): Promise<Project[]> {
  return mockProjectsRepo.getAll();
}

export async function getProjectById(id: string): Promise<Project | null> {
  return mockProjectsRepo.getById(id);
}

export async function createProject(input: CreateProjectInput): Promise<Project> {
  return mockProjectsRepo.create(input);
}

export async function updateProject(id: string, input: UpdateProjectInput): Promise<Project | null> {
  return mockProjectsRepo.update(id, input);
}
`,

    'src/app/page.tsx': `import { redirect } from 'next/navigation';

export default function Home() {
  redirect('/dashboard');
}
`,

    'src/components/projects/ProjectStatusBadge.tsx': `import { ProjectStatus } from '@/types';

export function ProjectStatusBadge({ status }: { status: ProjectStatus }) {
  const styles: Record<ProjectStatus, string> = {
    PLANNED: 'bg-slate-100 text-slate-700 border-slate-200',
    ACTIVE: 'bg-blue-50 text-blue-700 border-blue-200',
    ON_HOLD: 'bg-amber-50 text-amber-700 border-amber-200',
    COMPLETED: 'bg-green-50 text-green-700 border-green-200',
    CANCELLED: 'bg-red-50 text-red-700 border-red-200',
  };

  return (
    <span className={\`px-2.5 py-0.5 rounded-full text-xs font-medium border \${styles[status]}\`}>
      {status.replace('_', ' ')}
    </span>
  );
}
`,

    'src/components/projects/ProjectHealthBadge.tsx': `import { ProjectHealth } from '@/types';

export function ProjectHealthBadge({ health }: { health: ProjectHealth }) {
  const styles: Record<ProjectHealth, string> = {
    ON_TRACK: 'text-green-700 bg-green-50 border-green-200',
    AT_RISK: 'text-amber-700 bg-amber-50 border-amber-200',
    DELAYED: 'text-red-700 bg-red-50 border-red-200',
  };

  return (
    <span className={\`px-2.5 py-0.5 rounded-full text-xs font-medium border \${styles[health]}\`}>
      {health.replace('_', ' ')}
    </span>
  );
}
`,

    'src/components/projects/ProjectPriorityBadge.tsx': `import { ProjectPriority } from '@/types';

export function ProjectPriorityBadge({ priority }: { priority: ProjectPriority }) {
  const styles: Record<ProjectPriority, string> = {
    LOW: 'text-slate-600',
    MEDIUM: 'text-blue-600',
    HIGH: 'text-orange-600',
    CRITICAL: 'text-red-600 font-semibold',
  };

  return (
    <span className={\`text-xs \${styles[priority]}\`}>
      {priority}
    </span>
  );
}
`,

    'src/components/projects/CreateProjectDialog.tsx': `'use client';
import { useState } from 'react';
import { CreateProjectInput } from '@/types';
import { createProject } from '@/lib/api/projects';

interface Props {
  onProjectCreated: () => void;
  onClose: () => void;
}

export function CreateProjectDialog({ onProjectCreated, onClose }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    const formData = new FormData(e.currentTarget);
    
    const input: CreateProjectInput = {
      name: formData.get('name') as string,
      client: formData.get('client') as string,
      description: formData.get('description') as string,
      startDate: formData.get('startDate') as string,
      deadline: formData.get('deadline') as string,
      priority: formData.get('priority') as any,
      supervisorId: formData.get('supervisorId') as string,
    };
    
    if (new Date(input.deadline) < new Date(input.startDate)) {
      setError('Deadline cannot be before Start Date');
      setLoading(false);
      return;
    }

    try {
      await createProject(input);
      onProjectCreated();
      onClose();
    } catch (err) {
      setError('Failed to create project');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
          <h2 className="text-lg font-semibold text-slate-900">Create New Project</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">&times;</button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-4">
          {error && <div className="p-3 bg-red-50 text-red-600 text-sm rounded-md">{error}</div>}
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Project Name *</label>
            <input required name="name" type="text" className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Client *</label>
            <input required name="client" type="text" className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
            <textarea name="description" rows={3} className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"></textarea>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Start Date *</label>
              <input required name="startDate" type="date" className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Deadline *</label>
              <input required name="deadline" type="date" className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Priority *</label>
              <select required name="priority" className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white">
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Assign Supervisor *</label>
              <select required name="supervisorId" className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white">
                <option value="sup-1">Amit Sharma</option>
                <option value="sup-2">Neha Gupta</option>
                <option value="sup-3">Vikram Singh</option>
              </select>
            </div>
          </div>
          
          <div className="pt-4 flex justify-end space-x-3 border-t border-slate-100 mt-6">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-md hover:bg-slate-50">Cancel</button>
            <button type="submit" disabled={loading} className="px-4 py-2 text-sm font-medium text-white bg-slate-900 rounded-md hover:bg-slate-800 disabled:opacity-50">
              {loading ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
`,

    'src/components/projects/ProjectTable.tsx': `'use client';
import { Project } from '@/types';
import Link from 'next/link';
import { ProjectStatusBadge } from './ProjectStatusBadge';
import { ProjectHealthBadge } from './ProjectHealthBadge';
import { ProjectPriorityBadge } from './ProjectPriorityBadge';

export function ProjectTable({ projects }: { projects: Project[] }) {
  if (projects.length === 0) {
    return (
      <div className="text-center py-12 border border-slate-200 rounded-xl bg-white">
        <h3 className="text-lg font-medium text-slate-900">No projects yet</h3>
        <p className="text-sm text-slate-500 mt-1">Create your first project to start tracking company progress.</p>
      </div>
    );
  }

  return (
    <>
      <div className="hidden md:block overflow-x-auto bg-white border border-slate-200 rounded-xl shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500 border-b border-slate-200">
            <tr>
              <th className="px-6 py-4 font-medium uppercase tracking-wider text-xs">Project</th>
              <th className="px-6 py-4 font-medium uppercase tracking-wider text-xs">Client</th>
              <th className="px-6 py-4 font-medium uppercase tracking-wider text-xs">Progress</th>
              <th className="px-6 py-4 font-medium uppercase tracking-wider text-xs">Team</th>
              <th className="px-6 py-4 font-medium uppercase tracking-wider text-xs">Deadline</th>
              <th className="px-6 py-4 font-medium uppercase tracking-wider text-xs">Priority</th>
              <th className="px-6 py-4 font-medium uppercase tracking-wider text-xs">Health</th>
              <th className="px-6 py-4 font-medium uppercase tracking-wider text-xs">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {projects.map((project) => (
              <tr key={project.id} className="hover:bg-slate-50 transition-colors group">
                <td className="px-6 py-4">
                  <Link href={\`/projects/\${project.id}\`} className="font-medium text-slate-900 group-hover:text-blue-600 transition-colors">
                    {project.name}
                  </Link>
                </td>
                <td className="px-6 py-4 text-slate-600">{project.client}</td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-slate-900 rounded-full" style={{ width: \`\${project.progress}%\` }} />
                    </div>
                    <span className="text-xs text-slate-500">{project.progress}%</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-slate-600">{project.teamCount}</td>
                <td className="px-6 py-4 text-slate-600">{new Date(project.deadline).toLocaleDateString()}</td>
                <td className="px-6 py-4"><ProjectPriorityBadge priority={project.priority} /></td>
                <td className="px-6 py-4"><ProjectHealthBadge health={project.health} /></td>
                <td className="px-6 py-4"><ProjectStatusBadge status={project.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="md:hidden space-y-4">
        {projects.map(project => (
          <div key={project.id} className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <Link href={\`/projects/\${project.id}\`} className="font-medium text-slate-900 text-lg">
                {project.name}
              </Link>
              <ProjectStatusBadge status={project.status} />
            </div>
            <p className="text-sm text-slate-500 mb-4">{project.client}</p>
            <div className="grid grid-cols-2 gap-y-3 text-sm">
              <div>
                <span className="text-slate-400 block text-xs">Progress</span>
                <span className="font-medium">{project.progress}%</span>
              </div>
              <div>
                <span className="text-slate-400 block text-xs">Health</span>
                <ProjectHealthBadge health={project.health} />
              </div>
              <div>
                <span className="text-slate-400 block text-xs">Deadline</span>
                <span>{new Date(project.deadline).toLocaleDateString()}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-xs">Priority</span>
                <ProjectPriorityBadge priority={project.priority} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
`,

    'src/app/(app)/projects/page.tsx': `'use client';

import { useState, useEffect } from 'react';
import { Project } from '@/types';
import { getProjects } from '@/lib/api/projects';
import { ProjectTable } from '@/components/projects/ProjectTable';
import { CreateProjectDialog } from '@/components/projects/CreateProjectDialog';

// Mock Current User
const currentUser = { role: 'OWNER' };

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [toast, setToast] = useState('');

  const loadProjects = async () => {
    setLoading(true);
    const data = await getProjects();
    setProjects(data);
    setLoading(false);
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleProjectCreated = () => {
    loadProjects();
    setToast('Project created successfully!');
    setTimeout(() => setToast(''), 3000);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 relative">
      {toast && (
        <div className="fixed bottom-4 right-4 bg-slate-900 text-white px-4 py-2 rounded-md shadow-lg z-50 animate-in slide-in-from-bottom-5">
          {toast}
        </div>
      )}

      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-light text-slate-900 tracking-tight">Projects</h1>
          <p className="text-slate-500 mt-1">Manage active projects, monitor progress, and understand project health.</p>
        </div>
        {currentUser.role === 'OWNER' && (
          <button 
            onClick={() => setIsCreateOpen(true)}
            className="bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap"
          >
            + Create Project
          </button>
        )}
      </div>

      <div className="flex gap-4 flex-wrap bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <input type="text" placeholder="Search projects..." className="border border-slate-200 rounded-md px-3 py-1.5 text-sm outline-none focus:border-slate-400 w-full md:w-64" />
        <select className="border border-slate-200 rounded-md px-3 py-1.5 text-sm outline-none bg-white min-w-[120px]">
          <option value="">All Statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="COMPLETED">Completed</option>
        </select>
        <select className="border border-slate-200 rounded-md px-3 py-1.5 text-sm outline-none bg-white min-w-[120px]">
          <option value="">All Health</option>
          <option value="ON_TRACK">On Track</option>
          <option value="AT_RISK">At Risk</option>
          <option value="DELAYED">Delayed</option>
        </select>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center border border-slate-200 rounded-xl bg-white/50">
          <div className="text-slate-400">Loading projects...</div>
        </div>
      ) : (
        <ProjectTable projects={projects} />
      )}

      {isCreateOpen && (
        <CreateProjectDialog 
          onClose={() => setIsCreateOpen(false)} 
          onProjectCreated={handleProjectCreated}
        />
      )}
    </div>
  );
}
`,

    'src/app/(app)/projects/[id]/page.tsx': `import { getProjectById } from '@/lib/api/projects';
import { notFound } from 'next/navigation';
import { ProjectStatusBadge } from '@/components/projects/ProjectStatusBadge';
import { ProjectHealthBadge } from '@/components/projects/ProjectHealthBadge';
import { ProjectPriorityBadge } from '@/components/projects/ProjectPriorityBadge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

// Force dynamic rendering to always fetch latest mock data
export const dynamic = 'force-dynamic';

export default async function ProjectDetailsPage({ params }: { params: { id: string } }) {
  const project = await getProjectById(params.id);
  
  if (!project) {
    notFound();
  }

  // Mock Data for details
  const mockWork = [
    { id: 'w1', title: 'Create invoice API', status: 'COMPLETED', assignee: 'Rahul' },
    { id: 'w2', title: 'Payment gateway integration', status: 'IN_PROGRESS', assignee: 'Sneha' },
    { id: 'w3', title: 'Reservation API', status: 'BLOCKED', assignee: 'Vivek' },
  ];

  const mockBlockers = [
    { id: 'b1', title: 'Payment gateway credentials', age: '2 days', owner: 'Client' },
    { id: 'b2', title: 'API contract clarification', age: '1 day', owner: 'Backend Team' },
  ];

  const mockActivity = [
    'Rahul completed Invoice API',
    'Sneha updated Payment Integration',
    'Amit changed project priority to High',
    'Vivek reported a blocker',
    'Project progress updated to 76%'
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 sm:p-8 flex flex-col md:flex-row md:justify-between md:items-start gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-semibold text-slate-900 tracking-tight">{project.name}</h1>
            <ProjectStatusBadge status={project.status} />
          </div>
          <p className="text-slate-500 text-lg mb-6">{project.client}</p>
          
          <div className="flex flex-wrap gap-6 text-sm">
            <div>
              <span className="block text-slate-400 text-xs uppercase tracking-wider mb-1">Health</span>
              <ProjectHealthBadge health={project.health} />
            </div>
            <div>
              <span className="block text-slate-400 text-xs uppercase tracking-wider mb-1">Priority</span>
              <ProjectPriorityBadge priority={project.priority} />
            </div>
            <div>
              <span className="block text-slate-400 text-xs uppercase tracking-wider mb-1">Deadline</span>
              <span className="font-medium text-slate-700">{new Date(project.deadline).toLocaleDateString()}</span>
            </div>
            <div>
              <span className="block text-slate-400 text-xs uppercase tracking-wider mb-1">Supervisor</span>
              <span className="font-medium text-slate-700">Amit Sharma</span>
            </div>
          </div>
        </div>
        
        <div className="flex gap-3">
          <button className="px-4 py-2 border border-slate-200 text-slate-700 rounded-md text-sm font-medium hover:bg-slate-50 transition-colors">More Actions</button>
          <button className="px-4 py-2 bg-slate-900 text-white rounded-md text-sm font-medium hover:bg-slate-800 transition-colors">Edit Project</button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          
          {/* Progress & Overview */}
          <section>
            <h2 className="text-lg font-medium text-slate-900 mb-4">Project Overview</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="text-sm text-slate-500 mb-1">Progress</div>
                  <div className="text-2xl font-semibold text-slate-900">{project.progress}%</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-sm text-slate-500 mb-1">Total Work Items</div>
                  <div className="text-2xl font-semibold text-slate-900">42</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-sm text-slate-500 mb-1">Pending</div>
                  <div className="text-2xl font-semibold text-slate-900">18</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-sm text-slate-500 mb-1">Blocked</div>
                  <div className="text-2xl font-semibold text-red-600">2</div>
                </CardContent>
              </Card>
            </div>
            <div className="mt-4 bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-slate-900 h-full rounded-full" style={{ width: \`\${project.progress}%\` }}></div>
            </div>
          </section>

          {/* Work */}
          <section>
            <h2 className="text-lg font-medium text-slate-900 mb-4">Current Work</h2>
            <Card>
              <div className="divide-y divide-slate-100">
                {mockWork.map(work => (
                  <div key={work.id} className="p-4 flex items-center justify-between">
                    <div>
                      <div className="font-medium text-slate-900">{work.title}</div>
                      <div className="text-sm text-slate-500 mt-0.5">Assigned to: {work.assignee}</div>
                    </div>
                    <span className={\`text-xs px-2 py-1 rounded-md border \${
                      work.status === 'COMPLETED' ? 'bg-green-50 text-green-700 border-green-200' :
                      work.status === 'BLOCKED' ? 'bg-red-50 text-red-700 border-red-200' :
                      'bg-blue-50 text-blue-700 border-blue-200'
                    }\`}>
                      {work.status.replace('_', ' ')}
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          </section>

          {/* Blockers */}
          <section>
            <h2 className="text-lg font-medium text-red-600 mb-4">Active Blockers</h2>
            <div className="space-y-3">
              {mockBlockers.map(blocker => (
                <div key={blocker.id} className="bg-red-50/50 border border-red-100 p-4 rounded-xl">
                  <div className="font-medium text-slate-900 mb-1">{blocker.title}</div>
                  <div className="text-sm text-slate-600 flex gap-4">
                    <span>Waiting for: {blocker.owner}</span>
                    <span>Age: {blocker.age}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        <div className="space-y-8">
          {/* Team */}
          <section>
            <h2 className="text-lg font-medium text-slate-900 mb-4">Team</h2>
            <Card>
              <CardContent className="p-5 space-y-6">
                <div>
                  <div className="text-xs uppercase tracking-wider font-semibold text-slate-400 mb-3">Supervisor</div>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-slate-200"></div>
                    <div className="text-sm font-medium text-slate-900">Amit Sharma</div>
                  </div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wider font-semibold text-slate-400 mb-3">Team Leaders</div>
                  <div className="space-y-3">
                    {['Rahul Patil', 'Sneha Kulkarni', 'Vivek Joshi'].map(name => (
                      <div key={name} className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-slate-100"></div>
                        <div className="text-sm text-slate-700">{name}</div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="pt-4 border-t border-slate-100">
                  <div className="text-sm text-slate-600">
                    <span className="font-semibold text-slate-900">18</span> Active Workers
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Activity */}
          <section>
            <h2 className="text-lg font-medium text-slate-900 mb-4">Recent Activity</h2>
            <Card>
              <CardContent className="p-5">
                <div className="relative border-l border-slate-200 ml-3 space-y-6">
                  {mockActivity.map((act, i) => (
                    <div key={i} className="relative pl-6">
                      <div className="absolute -left-[5px] top-1.5 w-2 h-2 rounded-full bg-slate-300 ring-4 ring-white"></div>
                      <div className="text-sm text-slate-600">{act}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </section>
        </div>
      </div>
    </div>
  );
}
`
};

Object.keys(files).forEach(filepath => {
    ensureDirSync(path.dirname(filepath));
    fs.writeFileSync(filepath, files[filepath]);
});

console.log('Sprint 2 Setup complete.');
