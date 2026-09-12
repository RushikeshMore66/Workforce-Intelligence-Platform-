'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ReportScheduleForm } from './ReportScheduleForm';
import { ReportScheduleOut } from '@/types';

interface ReportScheduleDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialData?: ReportScheduleOut;
  onSuccess: () => void;
}

export function ReportScheduleDialog({ open, onOpenChange, initialData, onSuccess }: ReportScheduleDialogProps) {
  const handleSuccess = () => {
    onSuccess();
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{initialData ? 'Edit Schedule' : 'Create Schedule'}</DialogTitle>
        </DialogHeader>
        <ReportScheduleForm 
          initialData={initialData} 
          onSuccess={handleSuccess} 
          onCancel={() => onOpenChange(false)} 
        />
      </DialogContent>
    </Dialog>
  );
}
