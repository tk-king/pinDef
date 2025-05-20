import "./App.css";
import "@mantine/core/styles.css";
import '@mantine/notifications/styles.css';

import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ComponentCollector from './components/ComponentCollector';
import HomePage from './components/HomePage';
import HumanGrading from './components/HumanGrading';
import ViewComponents from './components/ViewComponents';

function App() {
  return (
    <MantineProvider>
      <Notifications />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/create" element={<ComponentCollector />} />
        <Route path="/human-grading" element={<HumanGrading />} />
        <Route path="/view-components" element={<ViewComponents />} />
      </Routes>
    </MantineProvider>
  );
}

export default App;
