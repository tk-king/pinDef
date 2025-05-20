import { useState } from "react";
import { notifications } from '@mantine/notifications';

const useCreateComponent = () => {
  const [component, setComponent] = useState({ pins: [] });

  const handleChange = (key, value) => {
    setComponent((prev) => ({ ...prev, [key]: value }));
  };

  const setPins = (newPins) => {
    setComponent((prev) => ({ ...prev, pins: newPins }));
  };

  const onSave = async () => {
    const res = await fetch("http://localhost:8000/components", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(component),
    });
    if (res.ok) {
      // alert("Component saved successfully!");
      notifications.show({
        title: 'Success',
        message: 'Component saved successfully!',
        color: 'green',
      });
      onClear();
    }
    else {
      // alert("Failed to save component.");
      notifications.show({
        title: 'Error',
        message: 'Failed to save component.',
        color: 'red',
      });
    }
  };

  const onClear = () => {
    console.log("Clearing component");
    setComponent({ pins: [] });
  };

  return {
    component,
    handleChange,
    setPins,
    onSave,
    onClear,
  };
};

export default useCreateComponent;
