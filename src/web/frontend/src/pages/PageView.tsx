import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { api } from '../api/client';
import type { Page } from '../types';

export function PageView() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [page, setPage] = useState<Page | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (slug) {
      api.getPage(slug).then((data) => {
        setPage(data);
        setLoading(false);
      }).catch(() => {
        setLoading(false);
      });
    }
  }, [slug]);

  const handleDelete = async () => {
    if (!slug || !confirm('Are you sure you want to delete this page?')) return;

    await api.deletePage(slug);
    navigate('/');
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  if (!page) {
    return <div className="text-center py-8">Page not found</div>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-4xl font-bold">{page.title}</h1>
        <div className="flex gap-2">
          <Link
            to={`/edit/${page.slug}`}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Edit
          </Link>
          <button
            onClick={handleDelete}
            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>

      {page.tags.length > 0 && (
        <div className="mb-4 flex gap-2">
          {page.tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      <div className="bg-white shadow rounded-lg p-6">
        <div className="prose max-w-none">
          <ReactMarkdown>{page.content}</ReactMarkdown>
        </div>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        <p>Created: {new Date(page.created_at).toLocaleString()}</p>
        <p>Updated: {new Date(page.updated_at).toLocaleString()}</p>
      </div>
    </div>
  );
}
