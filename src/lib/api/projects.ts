import { CreateProjectInput, Project, UpdateProjectInput } from '@/types';
import { mockProjectsRepo } from './mock/projects-repository';
import { TASKS } from '@/lib/mock-data/tasks';
import { BLOCKERS } from '@/lib/mock-data/blockers';
import { PROJECT_ACTIVITIES } from '@/lib/mock-data/activities';

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

export async function deleteProject(id: string): Promise<boolean> {
  return mockProjectsRepo.delete(id);
}

export async function getProjectTasks(projectId: string) {
  await new Promise(r => setTimeout(r, 200));
  return TASKS.filter(t => t.projectId === projectId);
}

export async function getProjectBlockers(projectId: string) {
  await new Promise(r => setTimeout(r, 200));
  return BLOCKERS.filter(b => b.projectId === projectId);
}

export async function getProjectActivities(projectId: string) {
  await new Promise(r => setTimeout(r, 200));
  return PROJECT_ACTIVITIES.filter(a => a.projectId === projectId);
}
