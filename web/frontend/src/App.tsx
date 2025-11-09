import { Route, Routes, Navigate } from "react-router-dom";
import { MainLayout } from "./layout/MainLayout";
import { Dashboard } from "./pages/Dashboard";
import { EnrollPage } from "./pages/Enroll";
import { VerifyPage } from "./pages/Verify";
import { UserDetailPage } from "./pages/UserDetail";

export function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/enroll" element={<EnrollPage />} />
        <Route path="/verify" element={<VerifyPage />} />
        <Route path="/user" element={<UserDetailPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;
