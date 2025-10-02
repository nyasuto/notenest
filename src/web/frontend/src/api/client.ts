import axios from 'axios';
import type { Page, PageCreate, PageUpdate, Tag, Plugin } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Pages
  async listPages(limit = 50, offset = 0): Promise<{ pages: Page[]; total: number }> {
    const response = await client.get('/pages', { params: { limit, offset } });
    return response.data;
  },

  async getPage(slug: string): Promise<Page> {
    const response = await client.get(`/pages/${slug}`);
    return response.data;
  },

  async createPage(data: PageCreate): Promise<Page> {
    const response = await client.post('/pages', data);
    return response.data;
  },

  async updatePage(slug: string, data: PageUpdate): Promise<Page> {
    const response = await client.put(`/pages/${slug}`, data);
    return response.data;
  },

  async deletePage(slug: string): Promise<void> {
    await client.delete(`/pages/${slug}`);
  },

  async getBacklinks(slug: string): Promise<{ pages: Page[]; total: number }> {
    const response = await client.get(`/pages/${slug}/backlinks`);
    return response.data;
  },

  // Tags
  async listTags(): Promise<Tag[]> {
    const response = await client.get('/tags');
    return response.data;
  },

  async getPagesByTag(tag: string): Promise<{ pages: Page[]; total: number }> {
    const response = await client.get(`/tags/${tag}/pages`);
    return response.data;
  },

  // Search
  async search(query: {
    q?: string;
    tags?: string[];
    metadata_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ pages: Page[]; total: number }> {
    const response = await client.post('/search', query);
    return response.data;
  },

  // Plugins
  async listPlugins(): Promise<Plugin[]> {
    const response = await client.get('/plugins');
    return response.data;
  },

  async getPluginSchema(metadataType: string): Promise<Record<string, any>> {
    const response = await client.get(`/plugins/metadata/${metadataType}/schema`);
    return response.data;
  },
};
