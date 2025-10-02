export interface Page {
  id: number;
  slug: string;
  title: string;
  content: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
  tags: string[];
}

export interface PageCreate {
  title: string;
  content: string;
  slug?: string;
  metadata?: Record<string, any>;
}

export interface PageUpdate {
  title?: string;
  content?: string;
  metadata?: Record<string, any>;
}

export interface Tag {
  name: string;
  count: number;
}

export interface Plugin {
  name: string;
  version: string;
  description: string;
  metadata_type?: string;
}
