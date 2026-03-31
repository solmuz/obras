import { formatInTimeZone } from 'date-fns-tz';
import { format, parseISO } from 'date-fns';

const DEFAULT_TIMEZONE = 'America/Bogota';

export const formatDateInTZ = (dateString: string, tz: string = DEFAULT_TIMEZONE): string => {
  try {
    const date = parseISO(dateString);
    return formatInTimeZone(date, tz, 'dd/MM/yyyy HH:mm:ss');
  } catch {
    return dateString;
  }
};

export const formatDateShort = (dateString: string, tz: string = DEFAULT_TIMEZONE): string => {
  try {
    const date = parseISO(dateString);
    return formatInTimeZone(date, tz, 'dd/MM/yyyy');
  } catch {
    return dateString;
  }
};

export const formatDateTimeLocal = (date: Date, tz: string = DEFAULT_TIMEZONE): string => {
  return formatInTimeZone(date, tz, 'dd/MM/yyyy HH:mm:ss');
};

export const getDaysUntil = (dateString: string): number => {
  const today = new Date();
  const targetDate = parseISO(dateString);
  const diffTime = targetDate.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
};

export const isExpired = (dateString: string): boolean => {
  return getDaysUntil(dateString) < 0;
};

export const getRelativeTime = (dateString: string): string => {
  const days = getDaysUntil(dateString);

  if (days < 0) return 'Vencido';
  if (days === 0) return 'Hoy';
  if (days === 1) return 'Mañana';
  if (days < 30) return `${days} días`;

  return formatDateShort(dateString);
};
