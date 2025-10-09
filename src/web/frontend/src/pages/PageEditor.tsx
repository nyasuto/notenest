import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { api } from '../api/client';
import type { Page, PageUpdate } from '../types';

type ViewMode = 'edit' | 'preview' | 'split';

export function PageEditor() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [page, setPage] = useState<Page | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('edit');

  useEffect(() => {
    if (slug) {
      api.getPage(slug).then((data) => {
        setPage(data);
        setTitle(data.title);
        setContent(data.content);
        setLoading(false);
      });
    }
  }, [slug]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!slug) return;

    const update: PageUpdate = {
      title,
      content,
    };

    await api.updatePage(slug, update);
    navigate(`/page/${slug}`);
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  if (!page) {
    return <div className="text-center py-8">Page not found</div>;
  }

  const renderEditor = () => (
    <div className="flex-1">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Content (Markdown)
      </label>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        rows={20}
        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2 border font-mono"
        required
      />
    </div>
  );

  const renderPreview = () => (
    <div className="flex-1">
      <label className="block text-sm font-medium text-gray-700 mb-2">Preview</label>
      <div className="prose max-w-none border rounded-md p-4 min-h-[500px] bg-white">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">Edit Page</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2 border"
            required
          />
        </div>

        {/* View Mode Selector */}
        <div className="flex gap-2 border-b pb-2">
          <button
            type="button"
            onClick={() => setViewMode('edit')}
            className={`px-4 py-2 rounded ${
              viewMode === 'edit'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Edit
          </button>
          <button
            type="button"
            onClick={() => setViewMode('preview')}
            className={`px-4 py-2 rounded ${
              viewMode === 'preview'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Preview
          </button>
          <button
            type="button"
            onClick={() => setViewMode('split')}
            className={`px-4 py-2 rounded ${
              viewMode === 'split'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Split View
          </button>
        </div>

        {/* Content Area */}
        <div className="flex gap-4">
          {viewMode === 'edit' && renderEditor()}
          {viewMode === 'preview' && renderPreview()}
          {viewMode === 'split' && (
            <>
              {renderEditor()}
              {renderPreview()}
            </>
          )}
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Save
          </button>
          <button
            type="button"
            onClick={() => navigate(`/page/${slug}`)}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
