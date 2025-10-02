import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import type { Tag } from '../types';

export function TagList() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listTags().then((data) => {
      setTags(data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">Tags</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {tags.map((tag) => (
          <Link
            key={tag.name}
            to={`/tag/${tag.name}`}
            className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow"
          >
            <h3 className="text-xl font-semibold text-blue-600">{tag.name}</h3>
            <p className="text-gray-600">{tag.count} pages</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
