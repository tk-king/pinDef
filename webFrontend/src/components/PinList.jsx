import { useState } from "react";
import {
  Card,
  Text,
  Group,
  ActionIcon,
  TextInput,
  Textarea,
  Button,
  Box,
  Stack,
  Center,
} from "@mantine/core";
import {
  IconGripVertical,
  IconTrash,
  IconPlus,
  IconCheck,
  IconX,
} from "@tabler/icons-react";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

// Sortable Pin Item Component
const SortablePin = ({ pin, onDelete, onSave }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedPin, setEditedPin] = useState({ ...pin });

  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({
      id: pin.id,
      disabled: isEditing,
    });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const handleChange = (field, value) => {
    setEditedPin({
      ...editedPin,
      [field]: value,
    });
  };

  const handleSave = () => {
    if (editedPin.number && editedPin.name) {
      onSave(editedPin);
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setEditedPin({ ...pin });
    setIsEditing(false);
  };

  // Allow editing on double click
  const handleDoubleClick = () => {
    if (!isEditing) {
      setIsEditing(true);
    }
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      onDoubleClick={handleDoubleClick}
    >
      <Card shadow="sm" p="sm" radius="md" withBorder mb="sm">
        {isEditing ? (
          <Stack spacing="xs">
            <Group position="apart">
              <TextInput
                size="xs"
                placeholder="Number"
                value={editedPin.number}
                onChange={(e) => handleChange("number", e.currentTarget.value)}
                required
                autoFocus
                style={{ width: "80px" }}
              />
              <Group spacing="xs">
                <ActionIcon color="green" onClick={handleSave}>
                  <IconCheck size={18} />
                </ActionIcon>
                <ActionIcon color="gray" onClick={handleCancel}>
                  <IconX size={18} />
                </ActionIcon>
              </Group>
            </Group>
            <TextInput
              size="sm"
              placeholder="Name"
              value={editedPin.name}
              onChange={(e) => handleChange("name", e.currentTarget.value)}
              required
            />
            <Textarea
              size="sm"
              placeholder="Description"
              value={editedPin.description}
              required
              onChange={(e) =>
                handleChange("description", e.currentTarget.value)
              }
              minRows={2}
            />
          </Stack>
        ) : (
          <>
            <Group position="apart" style={{ width: '100%' }}>
              <Group>
                <ActionIcon {...listeners}>
                  <IconGripVertical size={18} />
                </ActionIcon>
                <Group spacing="xs" align="center">
                  <Text fw={700}>Number:</Text>
                  <Text fw={500}>#{pin.number}</Text>
                  <Text fw={700} ml="md">Name:</Text>
                  <Text fw={500}>{pin.name}</Text>
                </Group>
              </Group>
              <div style={{ marginLeft: 'auto' }}>
                <ActionIcon color="red" onClick={() => onDelete(pin.id)}>
                  <IconTrash size={18} />
                </ActionIcon>
              </div>
            </Group>
            <Group mt="xs" spacing="xs" align="center">
              <Text fw={700}>Description:</Text>
              <Text size="sm" color="dimmed" style={{ whiteSpace: 'normal' }}>
                {pin.description}
              </Text>
            </Group>
          </>
        )}
      </Card>
    </div>
  );
};

const PinList = ({pins, setPins}) => {
  console.log(pins);

  const [newPin, setNewPin] = useState({
    number: "",
    name: "",
    description: "",
  });

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event) => {
    const { active, over } = event;

    if (active.id !== over.id) {
      setPins((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);

        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  const handleAddPin = () => {
    if (newPin.number && newPin.name) {
      const newPinWithId = {
        ...newPin,
        id: Date.now().toString(),
      };

      setPins([...pins, newPinWithId]);
      setNewPin({ number: "", name: "", description: "" });
    }
  };

  const handleDeletePin = (id) => {
    setPins(pins.filter((pin) => pin.id !== id));
  };

  const handlePinChange = (field, value) => {
    setNewPin({
      ...newPin,
      [field]: value,
    });
  };

  const handleSavePin = (updatedPin) => {
    setPins(pins.map((pin) => (pin.id === updatedPin.id ? updatedPin : pin)));
  };

  return (
    <Box p="md">
      <Stack spacing="md">
        <Card shadow="sm" p="md" radius="md" withBorder>
          <Text fw={500} size="lg" mb="md">
            Add New Pin
          </Text>
          <Group align="flex-start">
            <TextInput
              label="Number"
              placeholder="#"
              value={newPin.number}
              onChange={(event) =>
                handlePinChange("number", event.currentTarget.value)
              }
              required
              style={{ width: "80px" }}
            />
            <Textarea
              label="Name"
              placeholder="Pin name"
              value={newPin.name}
              onChange={(event) =>
                handlePinChange("name", event.currentTarget.value)
              }
              required
              autosize
              minRows={1}
              style={{ flex: 1 }}
            />
          </Group>
          <Textarea
            label="Description"
            placeholder="Pin description"
            value={newPin.description}
            onChange={(event) =>
              handlePinChange("description", event.currentTarget.value)
            }
            minRows={2}
            mt="xs"
          />
          <Button mt="md" onClick={handleAddPin} leftIcon={<IconPlus size={14} />} >
              Add
          </Button>
        </Card>

        {pins.length > 0 ? (
          <Card shadow="sm" p="md" radius="md" withBorder>
            <Text fw={500} size="lg" mb="md">
              Pin List (Double-click to edit)
            </Text>
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={handleDragEnd}
            >
              <SortableContext
                items={pins.map((pin) => pin.id)}
                strategy={verticalListSortingStrategy}
              >
                {pins.map((pin) => (
                  <SortablePin
                    key={pin.id}
                    pin={pin}
                    onDelete={handleDeletePin}
                    onSave={handleSavePin}
                  />
                ))}
              </SortableContext>
            </DndContext>
          </Card>
        ) : null}
      </Stack>
    </Box>
  );
};

export default PinList;
