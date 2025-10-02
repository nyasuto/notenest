import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import type { Page } from '../types';

export function PageList() {
  const [pages, setPages] = useState<Page[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listPages().then((data) => {
      setPages(data.pages);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">All Pages</h2>
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {pages.map((page) => (
            <li key={page.id}>
              <Link
                to={`/page/${page.slug}`}
                className="block hover:bg-gray-50 px-6 py-4"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{page.title}</h3>
                    <p className="text-sm text-gray-500">
                      Updated: {new Date(page.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                  {page.tags.length > 0 && (
                    <div className="flex gap-2">
                      {page.tags.map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
