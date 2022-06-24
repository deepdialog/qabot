
import './App.css';
import { Routes, Route } from "react-router-dom"
import 'antd/dist/antd.min.css'

import Home from './Home'
import Question from './Question'
import BatchInsert from './BatchInsert'

function App() {
    return (
        <div className="App">
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/home/:token" element={<Home />} />
                <Route path="/ask/:token" element={<Question />} />
                <Route path="/batch/:token" element={<BatchInsert />} />
            </Routes>
        </div>
    );
}

export default App
