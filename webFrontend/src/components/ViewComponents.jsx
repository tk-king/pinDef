import React, { useEffect, useState } from 'react';
import { Button, Group, Text, Flex, Center } from '@mantine/core';
import CreateComponent from './CreateComponent';
import PdfViewer from './PDFViewer';
import useCreateComponent from '../hooks/useCreateComponent';
import { isValidPDFUrl } from '../utils';

function ViewComponents() {
  const [components, setComponents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [jumpInput, setJumpInput] = useState(1);

  useEffect(() => {
    setJumpInput(currentIndex + 1);
  }, [currentIndex]);

  const { component, handleChange, setPins, onSave, onClear } = useCreateComponent();

  // Simple validation logic similar to CreateComponent's validation prop
  const validation = {
    url: component.url && component.url.length > 0 && !component.url.startsWith('http') ? 'Invalid URL' : null,
    pages: component.pages && isNaN(Number(component.pages)) ? 'Invalid page number' : null,
    name: component.name && component.name.length === 0 ? 'Invalid name' : null,
    manufacturer: component.manufacturer && component.manufacturer.length === 0 ? 'Invalid manufacturer' : null,
    version: component.version && component.version.length === 0 ? 'Invalid version' : null,
  };

  useEffect(() => {
    async function fetchComponents() {
      try {
        const response = await fetch('http://localhost:8000/components/');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setComponents(data);
        if (data.length > 0) {
          // Load first component into form
          loadComponent(data[0]);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchComponents();
  }, []);

  const loadComponent = (comp) => {
    // Load component data into useCreateComponent state
    handleChange('name', comp.name || '');
    handleChange('manufacturer', comp.manufacturer || '');
    handleChange('type', comp.type || '');
    handleChange('version', comp.version || '');
    handleChange('pages', comp.pages || '');
    handleChange('url', comp.url || '');
    setPins(comp.pins || []);
  };

  // eslint-disable-next-line no-unused-vars
  const handleJump = () => {
    const targetIndex = Number(jumpInput) - 1;
    if (targetIndex >= 0 && targetIndex < components.length) {
      setCurrentIndex(targetIndex);
      loadComponent(components[targetIndex]);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      const newIndex = currentIndex - 1;
      setCurrentIndex(newIndex);
      loadComponent(components[newIndex]);
    }
  };

  const handleNext = () => {
    if (currentIndex < components.length - 1) {
      const newIndex = currentIndex + 1;
      setCurrentIndex(newIndex);
      loadComponent(components[newIndex]);
    }
  };

  if (loading) {
    return <div>Loading components...</div>;
  }

  if (error) {
    return <div>Error loading components: {error}</div>;
  }

  if (components.length === 0) {
    return <p>No components found.</p>;
  }

  if (!component) {
    return <div>Loading component...</div>;
  }

  return (
    <div style={{ width: '100%', height: '100vh', overflow: 'hidden', margin: 0, padding: 0 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 20, width: '100%', padding: 0, boxSizing: 'border-box' }}>
        <Button onClick={handlePrev} disabled={currentIndex === 0}>
          Prev
        </Button>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <input
            type="number"
            value={jumpInput}
            onChange={(e) => setJumpInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleJump(); }}
            style={{ width: '50px', textAlign: 'center' }}
          />
          <Button onClick={handleJump} style={{ marginLeft: '8px' }}>Go</Button>
          <Text style={{ marginLeft: '8px' }}>&nbsp;/ {components.length}</Text>
        </div>
        <Button onClick={handleNext} disabled={currentIndex === components.length - 1}>
          Next
        </Button>
      </div>
      <Flex style={{ height: '90%', overflow: 'hidden' }}>
        <div style={{ width: '50%', overflow: 'auto' }}>
          <CreateComponent
            componentChange={handleChange}
            component={component}
            setPins={setPins}
            onSave={onSave}
            onClear={onClear}
            validation={validation}
          />
        </div>
        <div
          style={{
            width: '5px',
            cursor: 'ew-resize',
            background: '#ccc',
          }}
        />
        <div style={{ width: '50%', overflow: 'auto', height: '100%' }}>
          {isValidPDFUrl(component.url) ? (
            <PdfViewer url={'http://localhost:8000/components/pdf?name=' + component.name + "&" + 'url=' + component.url + (component.pages ? '#page=' + component.pages : '')} />
          ) : (
            <Center style={{ height: '100%' }}>
              <Text>Invalid PDF URL</Text>
            </Center>
          )}
        </div>
      </Flex>
    </div>
  );
}

export default ViewComponents;
