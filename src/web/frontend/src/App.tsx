import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { PageList } from './pages/PageList';
import { PageView } from './pages/PageView';
import { PageEditor } from './pages/PageEditor';
import { PageCreate } from './pages/PageCreate';
import { TagList } from './pages/TagList';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<PageList />} />
          <Route path="page/:slug" element={<PageView />} />
          <Route path="edit/:slug" element={<PageEditor />} />
          <Route path="create" element={<PageCreate />} />
          <Route path="tags" element={<TagList />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
