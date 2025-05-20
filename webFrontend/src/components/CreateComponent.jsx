import { useState } from "react";
import {
  Flex,
  TextInput,
  Box,
  Center,
  Card,
  Text,
  Button,
  Menu,
  Burger,
} from "@mantine/core";
import { IconDownload } from "@tabler/icons-react";
import PinList from "./PinList";
import useComponents from "../hooks/useComponents";
import { isValidPageNumber, isValidPDFUrl } from "../utils";
import { TypeSelect } from "./TypeSelect";

const CreateComponent = ({
  componentChange,
  component,
  setPins,
  onSave,
  onClear,
  validation,
}) => {
  const [opened, setOpened] = useState(false);

  const { downloadAll } = useComponents();

  console.log(component);
  return (
    <div>
      <Flex direction="row" justify="space-between" align="center" mx="md">
        <h3>Create Component</h3>
        <Menu shadow="md" width={200} position="bottom-end">
          <Menu.Target>
            <Burger
              opened={opened}
              onClick={() => setOpened((o) => !o)}
              size="sm"
              aria-label="Toggle menu"
            />
          </Menu.Target>
          <Menu.Dropdown>
            <Menu.Item icon={<IconDownload size={16} />} onClick={downloadAll}>
              Download All
            </Menu.Item>
          </Menu.Dropdown>
        </Menu>
      </Flex>
      <Box p="md">
        <Card p="md" radius="md" withBorder>
          <Flex justify="space-between" align="center" mb="md">
            <Text fw={500} fz="lg" mb="md">
              General information
            </Text>
            <Flex gap={"md"}>
              <Button onClick={onClear}>Clear</Button>
              <Button color="green" onClick={onSave}>
                Save
              </Button>
            </Flex>
          </Flex>
          <Flex gap="md">
            <TextInput
              error={validation.url}
              label="Datasheet URL"
              placeholder="Datasheet URL"
              required
              value={component.url ? component.url : ""}
              style={{ flex: 3 }}
              onChange={(event) =>
                componentChange("url", event.currentTarget.value)
              }
            />
            <TextInput
              label="Version"
              error={
                component.version && component.version.length > 0
                  ? null
                  : "Invalid version"
              }
              placeholder="Datasheet Version"
              required
              value={component.version ? component.version : ""}
              style={{ flex: 1 }}
              onChange={(event) =>
                componentChange("version", event.currentTarget.value)
              }
            />
          </Flex>
          <Flex gap="md">
            <TextInput
              error={
                component.name &&
                !isValidPDFUrl(component.name) &&
                component.name.length > 0
                  ? null
                  : "Invalid name"
              }
              label="Component Name"
              placeholder="Component Name"
              required
              style={{ flex: 3 }}
              value={component.name ? component.name : ""}
              onChange={(event) =>
                componentChange("name", event.currentTarget.value)
              }
            />
            <TextInput
              label="Manufacturer"
              placeholder="Component Manufacturer"
              required
              error={
                component.manufacturer &&
                !isValidPDFUrl(component.manufacturer) &&
                component.manufacturer.length > 0
                  ? null
                  : "Invalid manufacturer"
              }
              style={{ flex: 3 }}
              value={component.manufacturer ? component.manufacturer : ""}
              onChange={(event) =>
                componentChange("manufacturer", event.currentTarget.value)
              }
            />
          </Flex>
          <Flex gap="md">
            <div>
              <TypeSelect
                selected={component.type}
                setSelected={(type) => componentChange("type", type)}
              ></TypeSelect>
            </div>
            {/* <TextInput
              label="Component Type"
              placeholder="Component Type"
              required
              error={component.type && !isValidPDFUrl(component.type) && component.type.length > 0 ? null : "Invalid type"}
              style={{ flex: 3 }}
              value={component.type ? component.type : ""}
              onChange={(event) =>
                componentChange("type", event.currentTarget.value)
              }
            /> */}
            <TextInput
              error={
                isValidPageNumber(component.pages)
                  ? null
                  : "Invalid page number"
              }
              label="Page Numbers"
              placeholder="Page Numbers"
              required
              style={{ flex: 3 }}
              value={component.pages ? component.pages : ""}
              onChange={(event) =>
                componentChange("pages", event.currentTarget.value)
              }
            ></TextInput>
          </Flex>
        </Card>
      </Box>
      <PinList pins={component.pins} setPins={setPins}></PinList>
    </div>
  );
};

export default CreateComponent;
