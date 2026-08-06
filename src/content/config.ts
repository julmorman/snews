import { defineCollection, z } from 'astro:content';

const newsCollection = defineCollection({
  type: 'data',
  schema: z.object({
    id: z.string(),
    funny_title: z.string(),
    date: z.string(),
    intro_label: z.string().optional(),
    map_caption: z.string().optional(),
    map_points: z.array(z.object({
      label: z.string(),
      lat: z.number(),
      lng: z.number(),
      newsId: z.string(),
      labelPos: z.enum(['top', 'bottom', 'left', 'right']).optional(),
    })).optional(),
    news: z.array(z.object({
      id: z.string(),
      category: z.string(),
      title: z.string(),
      presentation_title: z.string().optional(),
      short_summary: z.string(),
      context: z.string(),
      extended_context: z.string().optional(),
      links: z.array(z.object({
        name: z.string(),
        url: z.string().url(),
      })),
      color: z.string().optional(),
      image: z.string().url(),
      related_terms: z.array(z.string()).optional(),
      timeline: z.array(z.object({
        date: z.string(),
        text: z.string(),
      })).optional(),
    })),
  }),
});

const glossaryCollection = defineCollection({
  type: 'data',
  schema: z.object({
    id: z.string(),
    term: z.string(),
    short_description: z.string(),
    sections: z.array(z.object({
      heading: z.string().optional(),
      text: z.string(),
    })),
    images: z.array(z.object({
      url: z.string().url(),
      caption: z.string().optional(),
    })).optional(),
    sources: z.array(z.object({
      name: z.string(),
      url: z.string().url(),
    })).optional(),
  }),
});

export const collections = {
  'news': newsCollection,
  'glosario': glossaryCollection,
};
