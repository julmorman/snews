export const SITE_TITLE = 'The Loop';
export const SITE_DESCRIPTION = 'Noticias que importan, explicadas para que formes tu propia opinión.';
export const SITE_URL = 'https://the-weekly-loop.vercel.app';

export const CATEGORIES = [
  {
    id: 'geopolítica',
    label: 'GLOBAL',
    color: '#ef4444'
  },
  {
    id: 'nacional',
    label: 'NACIONAL',
    color: '#3eaaf7'
  },
  {
    id: 'ciencias',
    label: 'CIENCIAS',
    color: '#06b6d4'
  },
  {
    id: 'sustentabilidad',
    label: 'SUSTENTABILIDAD',
    color: '#10b981'
  }
];

export const getCategoryColor = (categoryId: string) => {
  const category = CATEGORIES.find(c => c.id === categoryId.toLowerCase());
  return category ? category.color : '#3b82f6';
};
