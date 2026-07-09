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
    id: 'ciencia-ambiente',
    label: 'CIENCIA & AMBIENTE',
    color: '#14b8a6'
  },
  {
    id: 'negocios-tecnologia',
    label: 'NEGOCIOS & TECNOLOGÍA',
    color: '#f59e0b'
  },
  {
    id: 'opinión',
    label: 'OPINIÓN',
    color: '#8b5cf6'
  }
];

export const normalizeCategory = (cat: string) => {
  return cat.toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/s$/, ''); // maps 'ciencias' to 'ciencia' or vice versa just in case
};

export const matchCategory = (catA: string, catB: string) => {
  return normalizeCategory(catA) === normalizeCategory(catB);
};

export const getCategoryColor = (categoryId: string) => {
  const category = CATEGORIES.find(c => matchCategory(c.id, categoryId));
  return category ? category.color : '#3b82f6';
};

