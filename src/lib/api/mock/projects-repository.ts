import { ProjectViewModel, CreateProjectInput, UpdateProjectInput } from '@/types';
import { INITIAL_PROJECTS } from '@/lib/mock-data/projects';

const STORAGE_KEY = 'wi_mock_projects_v2';

function delay(ms = 300) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class ProjectsRepository {
  private getProjects(): ProjectViewModel[] {
    if (typeof window === 'undefined') return INITIAL_PROJECTS;
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_PROJECTS));
      return INITIAL_PROJECTS;
    }
    try {
      return JSON.parse(stored) as ProjectViewModel[];
    } catch {
      return INITIAL_PROJECTS;
    }
  }

  private saveProjects(projects: ProjectViewModel[]) {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
    }
  }

  async getAll(): Promise<ProjectViewModel[]> {
    await delay(300);
    return this.getProjects();
  }

  async getById(id: string): Promise<ProjectViewModel | null> {
    await delay(200);
    return this.getProjects().find(p => p.id === id) ?? null;
  }

  async create(input: CreateProjectInput): Promise<ProjectViewModel> {
    await delay(500);
    const projects = this.getProjects();
    const newProject: ProjectViewModel = {
      ...input,
      id: `proj-${Date.now()}`,
      status: 'PLANNED',
      health: 'ON_TRACK',
      progress: 0,
      teamCount: 0,
      createdAt: new Date().toISOString(),
    };
    this.saveProjects([...projects, newProject]);
    return newProject;
  }

  async update(id: string, input: UpdateProjectInput): Promise<ProjectViewModel | null> {
    await delay(400);
    const projects = this.getProjects();
    const idx = projects.findIndex(p => p.id === id);
    if (idx === -1) return null;
    const updated = { ...projects[idx], ...input };
    projects[idx] = updated;
    this.saveProjects(projects);
    return updated;
  }

  async delete(id: string): Promise<boolean> {
    await delay(400);
    const projects = this.getProjects();
    const filtered = projects.filter(p => p.id !== id);
    if (filtered.length === projects.length) return false;
    this.saveProjects(filtered);
    return true;
  }
}

export const mockProjectsRepo = new ProjectsRepository();
