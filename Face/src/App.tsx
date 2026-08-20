import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import SignIn from "./pages/sign_in";
import ChatArea from "./pages/chat_area";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/chat" element={<ChatArea />} />
      </Routes>
    </Router>
  );
}

export default App;