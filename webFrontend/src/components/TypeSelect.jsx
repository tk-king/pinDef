import { useState, useEffect } from "react";
import { Button, Menu, Box, Text, Paper, MenuLabel, InputLabel } from "@mantine/core";
import { IconChevronRight } from "@tabler/icons-react";
import yaml from "js-yaml";

export function TypeSelect({ selected, setSelected }) {
  const [hoveredL1, setHoveredL1] = useState(null);
  const [hoveredL2, setHoveredL2] = useState(null);
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("/types.yaml")
      .then((res) => res.text())
      .then((text) => {
        const parsed = yaml.load(text);
        setData(parsed);
      });
  }, []);

  const handleSelect = (...args) => {
    setSelected(args.join(", "));
  };

  console.log("selected", selected);
  return (
    <>
      <Menu
        width={200}
        shadow="md"
        position="bottom-start"
        closeOnItemClick={false}
      >
        
        
        <div><InputLabel required>Type</InputLabel></div>
        <Menu.Target>
          <Button>{selected ? selected : "Choose item"}</Button>
        </Menu.Target>

        <Menu.Dropdown>
          {data.map((level1) => (
            <Box
              key={level1.label}
              onMouseEnter={() => setHoveredL1(level1.label)}
              onMouseLeave={() => setHoveredL1(null)}
              style={{ position: "relative" }}
            >
              <Menu.Item rightSection={<IconChevronRight size={16} />}>
                {level1.label}
              </Menu.Item>

              {hoveredL1 === level1.label && (
                <Paper
                  shadow="md"
                  withBorder
                  style={{
                    position: "absolute",
                    top: 0,
                    left: "100%",
                    zIndex: 1000,
                  }}
                >
                  {level1.children &&
                    level1.children.map((level2) => {
                      const isTerminalL2 = !level2.children;

                      return (
                        <Box
                          key={level2.label}
                          onMouseEnter={() => setHoveredL2(level2.label)}
                          onMouseLeave={() => setHoveredL2(null)}
                          style={{ position: "relative" }}
                        >
                          {isTerminalL2 ? (
                            <Menu.Item
                              onClick={() =>
                                handleSelect(level1.label, level2.label)
                              }
                            >
                              {level2.label}
                            </Menu.Item>
                          ) : (
                            <Menu.Item
                              rightSection={<IconChevronRight size={16} />}
                            >
                              {level2.label}
                            </Menu.Item>
                          )}

                          {!isTerminalL2 && hoveredL2 === level2.label && (
                            <Paper
                              shadow="md"
                              withBorder
                              style={{
                                position: "absolute",
                                top: 0,
                                left: "100%",
                                zIndex: 1001,
                              }}
                            >
                              {level2.children.map((item) => (
                                <Menu.Item
                                  key={item}
                                  onClick={() =>
                                    handleSelect(
                                      level1.label,
                                      level2.label,
                                      item
                                    )
                                  }
                                >
                                  {item}
                                </Menu.Item>
                              ))}
                            </Paper>
                          )}
                        </Box>
                      );
                    })}
                </Paper>
              )}
            </Box>
          ))}
        </Menu.Dropdown>
      </Menu>
    </>
  );
}
