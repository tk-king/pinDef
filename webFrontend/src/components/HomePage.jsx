import React from 'react';
import { Button, Container, Title } from '@mantine/core';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Container style={{ height: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
      <Title order={2} mb="md">Welcome to the PCB Component Collection</Title>
      <div style={{ display: 'flex', gap: '16px' }}>
        <Button size="lg" onClick={() => navigate('/create')} style={{ backgroundColor: '#4caf50', borderColor: '#4caf50' }}>
          Go to Create Component
        </Button>
        <Button size="lg" onClick={() => navigate('/human-grading')} style={{ backgroundColor: '#2196f3', borderColor: '#2196f3' }}>
          Human Grading
        </Button>
        <Button size="lg" onClick={() => navigate('/view-components')} style={{ backgroundColor: '#ff5722', borderColor: '#ff5722' }}>
          View Components
        </Button>
      </div>
    </Container>
  );
};

export default HomePage;
