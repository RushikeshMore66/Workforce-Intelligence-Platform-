'use client';
import { useState } from 'react';
import { CreateProjectInput } from '@/types';
import { createProject } from '@/lib/api/projects';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogDescription, DialogFooter, DialogBody,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input, Textarea, Label, FormField, FormError } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const SUPERVISORS = [
  { id: 'sup-1', name: 'Amit Sharma' },
  { id: 'sup-2', name: 'Priya Deshmukh' },
  { id: 'sup-3', name: 'Rahul Mehta' },
  { id: 'sup-4', name: 'Neha Kulkarni' },
  { id: 'sup-5', name: 'Vikram Patil' },
];

interface Props {
  onClose: () => void;
  onProjectCreated: () => void;
}

export function CreateProjectDialog({ onClose, onProjectCreated }: Props) {
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState('');
  const [form, setForm] = useState({
    name: '', client: '', description: '',
    startDate: '', deadline: '',
    priority: '' as CreateProjectInput['priority'] | '',
    supervisorId: '',
  });

  function set(field: string, value: string) {
    setForm(f => ({ ...f, [field]: value }));
    setErrors(e => ({ ...e, [field]: '' }));
  }

  function validate(): boolean {
    const newErrors: Record<string, string> = {};
    if (!form.name.trim())       newErrors.name       = 'Project name is required';
    if (!form.client.trim())     newErrors.client     = 'Client is required';
    if (!form.startDate)         newErrors.startDate  = 'Start date is required';
    if (!form.deadline)          newErrors.deadline   = 'Deadline is required';
    if (!form.priority)          newErrors.priority   = 'Priority is required';
    if (!form.supervisorId)      newErrors.supervisorId = 'Supervisor is required';
    if (form.startDate && form.deadline && form.deadline < form.startDate)
      newErrors.deadline = 'Deadline cannot be before start date';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setServerError('');
    try {
      await createProject(form as CreateProjectInput);
      onProjectCreated();
      onClose();
    } catch {
      setServerError('Failed to create project. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <Dialog open onOpenChange={open => !open && onClose()}>
      <DialogContent size="md">
        <DialogHeader>
          <DialogTitle>Create New Project</DialogTitle>
          <DialogDescription>Fill in the project details below. All starred fields are required.</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <DialogBody className="space-y-4">
            {serverError && (
              <div className="p-3 bg-[#FEF3F2] border border-[#FECDCA] rounded-lg text-sm text-[#B42318]">
                {serverError}
              </div>
            )}

            <FormField>
              <Label required>Project Name</Label>
              <Input
                value={form.name}
                onChange={e => set('name', e.target.value)}
                placeholder="e.g. Hotel Billing System v2"
              />
              <FormError message={errors.name} />
            </FormField>

            <FormField>
              <Label required>Client</Label>
              <Input
                value={form.client}
                onChange={e => set('client', e.target.value)}
                placeholder="e.g. Grand Hotels & Resorts"
              />
              <FormError message={errors.client} />
            </FormField>

            <FormField>
              <Label>Description</Label>
              <Textarea
                value={form.description}
                onChange={e => set('description', e.target.value)}
                rows={3}
                placeholder="Brief project overview..."
              />
            </FormField>

            <div className="grid grid-cols-2 gap-4">
              <FormField>
                <Label required>Start Date</Label>
                <Input
                  type="date"
                  value={form.startDate}
                  onChange={e => set('startDate', e.target.value)}
                />
                <FormError message={errors.startDate} />
              </FormField>
              <FormField>
                <Label required>Deadline</Label>
                <Input
                  type="date"
                  value={form.deadline}
                  onChange={e => set('deadline', e.target.value)}
                />
                <FormError message={errors.deadline} />
              </FormField>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField>
                <Label required>Priority</Label>
                <Select value={form.priority} onValueChange={v => set('priority', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select priority" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="LOW">Low</SelectItem>
                    <SelectItem value="MEDIUM">Medium</SelectItem>
                    <SelectItem value="HIGH">High</SelectItem>
                    <SelectItem value="CRITICAL">Critical</SelectItem>
                  </SelectContent>
                </Select>
                <FormError message={errors.priority} />
              </FormField>

              <FormField>
                <Label required>Supervisor</Label>
                <Select value={form.supervisorId} onValueChange={v => set('supervisorId', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select supervisor" />
                  </SelectTrigger>
                  <SelectContent>
                    {SUPERVISORS.map(s => (
                      <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormError message={errors.supervisorId} />
              </FormField>
            </div>
          </DialogBody>

          <DialogFooter>
            <Button type="button" variant="secondary" onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" loading={loading}>
              {loading ? 'Creating...' : 'Create Project'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
