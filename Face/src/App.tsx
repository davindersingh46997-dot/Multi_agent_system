import { BrowserRouter as Router, Navigate, Route, Routes } from "react-router-dom";
import SignIn from "./pages/sign_in";
import SignUp from "./pages/SignUp";
import AgenticWorkspace from "./pages/agentic_workspace";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/workspace" element={<AgenticWorkspace />} />
        <Route path="/login/chat" element={<Navigate to="/workspace" replace />} />
        <Route path="/chat" element={<Navigate to="/workspace" replace />} />
        <Route path="/SignUp" element={<SignUp/>} />
        <Route path="/login" element={<SignIn/>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;