import { SemaforoStatus } from '@/types';

export const calculateSemaforoStatus = (
  externalInspectionDate: string | undefined,
  siteInspectionDate: string | undefined,
  isDecommissioned: boolean
): SemaforoStatus => {
  if (isDecommissioned) return SemaforoStatus.ROJO;

  const today = new Date();
  const thirtyDaysFromNow = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);

  const externalDate = externalInspectionDate ? new Date(externalInspectionDate) : null;
  const siteDate = siteInspectionDate ? new Date(siteInspectionDate) : null;

  // If either is expired, it's RED
  if ((externalDate && externalDate < today) || (siteDate && siteDate < today)) {
    return SemaforoStatus.ROJO;
  }

  // If both exist and either is within 30 days, it's YELLOW
  if (externalDate && siteDate) {
    if (externalDate < thirtyDaysFromNow || siteDate < thirtyDaysFromNow) {
      return SemaforoStatus.AMARILLO;
    }
  }

  return SemaforoStatus.VERDE;
};

export const getColorForStatus = (status: SemaforoStatus): string => {
  switch (status) {
    case SemaforoStatus.VERDE:
      return '#10b981';
    case SemaforoStatus.AMARILLO:
      return '#f59e0b';
    case SemaforoStatus.ROJO:
      return '#ef4444';
    default:
      return '#999999';
  }
};

export const getLabelForStatus = (status: SemaforoStatus): string => {
  switch (status) {
    case SemaforoStatus.VERDE:
      return 'Vigente';
    case SemaforoStatus.AMARILLO:
      return 'Por Vencer';
    case SemaforoStatus.ROJO:
      return 'Vencido';
    default:
      return 'Desconocido';
  }
};
