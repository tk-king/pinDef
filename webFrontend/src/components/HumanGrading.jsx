import React, { useState, useEffect } from "react";
import { Container, Title, Text, Button, Checkbox, Group, Loader, Notification, Progress, Card, Divider } from "@mantine/core";
import { useNavigate } from "react-router-dom";

const HumanGrading = () => {
  const navigate = useNavigate();
  const [pins, setPins] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [nameCorrect, setNameCorrect] = useState(null);
  const [descriptionCorrect, setDescriptionCorrect] = useState(null);
  const [submitStatus, setSubmitStatus] = useState(null);

  useEffect(() => {
    const fetchPins = async () => {
      try {
        const response = await fetch("http://localhost:8000/random_grading/");
        if (!response.ok) {
          throw new Error("Failed to fetch pins");
        }
        const data = await response.json();
        setPins(data);
        setLoading(false);
        if (data.length > 0) {
          // Initialize nameCorrect and descriptionCorrect from expert_grading fields
          setNameCorrect(data[0].expert_grading?.expert_name_correct ?? null);
          setDescriptionCorrect(data[0].expert_grading?.expert_description_correct ?? null);
        }
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };
    fetchPins();
  }, []);

  // New useEffect to update grading states when currentIndex or pins change
  useEffect(() => {
    if (pins.length > 0 && currentIndex >= 0 && currentIndex < pins.length) {
      setNameCorrect(pins[currentIndex].expert_grading?.expert_name_correct ?? null);
      setDescriptionCorrect(pins[currentIndex].expert_grading?.expert_description_correct ?? null);
      setSubmitStatus(null);
    }
  }, [currentIndex, pins]);

  const handleNext = async () => {
    if (currentIndex < 0 || currentIndex >= pins.length) return;

    // Save current grading before moving to next
    const pinToUpdate = pins[currentIndex];
    const updatedPin = {
      ...pinToUpdate,
      expert_grading: {
        expert_name_correct: nameCorrect,
        expert_description_correct: descriptionCorrect,
      },
    };

    try {
      const response = await fetch("http://localhost:8000/random_grading/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedPin),
      });
      if (!response.ok) {
        throw new Error("Failed to submit grading");
      }
      setSubmitStatus("Grading submitted successfully");
      // Update local state
      const newPins = [...pins];
      newPins[currentIndex] = updatedPin;
      setPins(newPins);

      // Move to next pin
      if (currentIndex < pins.length - 1) {
        setCurrentIndex(currentIndex + 1);
        // Initialize nameCorrect and descriptionCorrect from next pin's expert_grading fields using updated pins array
        // setNameCorrect(newPins[currentIndex + 1].expert_grading?.expert_name_correct ?? null);
        // setDescriptionCorrect(newPins[currentIndex + 1].expert_grading?.expert_description_correct ?? null);
        // setSubmitStatus(null);
      }
    } catch (err) {
      setSubmitStatus(`Error: ${err.message}`);
    }
  };

  const handleBack = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      // Initialize nameCorrect and descriptionCorrect from previous pin's expert_grading fields
      // setNameCorrect(pins[currentIndex - 1].expert_grading?.expert_name_correct ?? null);
      // setDescriptionCorrect(pins[currentIndex - 1].expert_grading?.expert_description_correct ?? null);
      // setSubmitStatus(null);
    }
  };

  if (loading) {
    return (
      <Container style={{ height: "100vh", display: "flex", justifyContent: "center", alignItems: "center" }}>
        <Loader size="xl" />
      </Container>
    );
  }

  if (error) {
    return (
      <Container style={{ height: "100vh", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
        <Notification color="red" title="Error" disallowClose>
          {error}
        </Notification>
        <Button mt="md" onClick={() => navigate('/')}>Back to Home</Button>
      </Container>
    );
  }

  if (pins.length === 0) {
    return (
      <Container style={{ height: "100vh", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
        <Text>No pins available for grading.</Text>
        <Button mt="md" onClick={() => navigate('/')}>Back to Home</Button>
      </Container>
    );
  }

  const currentPin = pins[currentIndex];
  const progress = ((currentIndex + 1) / pins.length) * 100;

  return (
    <Container style={{ height: "100vh", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
      <Title order={2} mb="md">Human Grading Page</Title>
      <Progress value={progress} size="xl" mb="lg" style={{ width: "100%", maxWidth: 600 }} />

      <Card shadow="sm" padding="lg" style={{ width: "100%", maxWidth: 600 }}>
        <Divider my="sm" />
        <Text weight={500}>Name Comparison</Text>
        <Text><strong>LLM Pin Name:</strong> {currentPin.llm_pins?.name || "N/A"}</Text>
        <Text><strong>Human Pin Name:</strong> {currentPin.human_pin?.name || "N/A"}</Text>
        <Checkbox
          label="Names match"
          checked={nameCorrect === true}
          indeterminate={nameCorrect === null}
          onChange={(event) => setNameCorrect(event.currentTarget.checked)}
          mt="sm"
          mb="md"
        />
        <Divider my="sm" />
        <Text weight={500}>Description Comparison</Text>
        <Text><strong>LLM Pin Description:</strong> {currentPin.llm_pins?.description || "N/A"}</Text>
        <Text><strong>Human Pin Description:</strong> {currentPin.human_pin?.description || "N/A"}</Text>
        <Checkbox
          label="Descriptions match"
          checked={descriptionCorrect === true}
          indeterminate={descriptionCorrect === null}
          onChange={(event) => setDescriptionCorrect(event.currentTarget.checked)}
          mt="sm"
          mb="md"
        />

        <Group position="apart" mt="md">
          <Button onClick={handleBack} disabled={currentIndex <= 0}>Back</Button>
          <Button
            onClick={handleNext}
            disabled={
              currentIndex >= pins.length - 1 ||
              nameCorrect === null ||
              descriptionCorrect === null
            }
          >
            Next Pin
          </Button>
        </Group>

      <Button onClick={() => navigate('/')} style={{ position: "fixed", bottom: 20, right: 20 }}>
        Back to Home
      </Button>

        {submitStatus && <Text mt="md">{submitStatus}</Text>}
      </Card>
    </Container>
  );
};

export default HumanGrading;
