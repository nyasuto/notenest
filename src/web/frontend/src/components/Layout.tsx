import { Link, Outlet } from 'react-router-dom';

export function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">
              <Link to="/">NoteNest</Link>
            </h1>
            <nav className="flex gap-4">
              <Link to="/" className="text-gray-600 hover:text-gray-900">
                Pages
              </Link>
              <Link to="/tags" className="text-gray-600 hover:text-gray-900">
                Tags
              </Link>
              <Link to="/create" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                New Page
              </Link>
            </nav>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
