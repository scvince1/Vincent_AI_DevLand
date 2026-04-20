import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { OverviewPage } from './pages/OverviewPage';
import { ProductAnalysisPage } from './pages/ProductAnalysisPage';
import { PlatformComparisonPage } from './pages/PlatformComparisonPage';
import { TopicExplorerPage } from './pages/TopicExplorerPage';
import { AlertsInsightsPage } from './pages/AlertsInsightsPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<OverviewPage />} />
          <Route path="products" element={<ProductAnalysisPage />} />
          <Route path="platforms" element={<PlatformComparisonPage />} />
          <Route path="topics" element={<TopicExplorerPage />} />
          <Route path="alerts" element={<AlertsInsightsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App
