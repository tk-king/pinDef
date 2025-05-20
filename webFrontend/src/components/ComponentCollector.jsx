import React, { useState } from "react";
import CreateComponent from "./CreateComponent";
import PdfViewer from "./PDFViewer";
import { Center, Flex, Text } from "@mantine/core";
import { isValidPDFUrl, isValidPageNumber } from "../utils";
import useCreateComponent from "../hooks/useCreateComponent";

const ComponentCollector = () => {
  const [leftWidth, setLeftWidth] = useState(50); // Percentage of CreateComponent width

  const { component, handleChange, setPins, onSave, onClear, toast} = useCreateComponent();

  const handleDrag = (e) => {
    const newWidth = (e.clientX / window.innerWidth) * 100;
    if (newWidth > 20 && newWidth < 80) {
      // Limit resizing
      setLeftWidth(newWidth);
    }
  };

  const validation = {
    url: isValidPDFUrl(component.url) && component.url !== "" ? null : "Invalid PDF URL",
    pages: isValidPageNumber(component.page) && component.page !== "" ? null : "Invalid page number", 
  }

  console.log("Validation")
  console.log(validation)

  return (
    <div style={{ width: "100vw", height: "100vh", overflow: "hidden" }}>
      <Flex style={{ height: "100%" }}>
        <div style={{ width: `${leftWidth}%`, overflow: "auto" }}>
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
          style={{ width: "5px", cursor: "ew-resize", background: "#ccc" }}
          onMouseDown={() => {
            document.addEventListener("mousemove", handleDrag);
            document.addEventListener(
              "mouseup",
              () => {
                document.removeEventListener("mousemove", handleDrag);
              },
              { once: true }
            );
          }}
        />
        <div
          style={{
            width: `${100 - leftWidth}%`,
            overflow: "auto",
            height: "100%",
          }}
        >
          {isValidPDFUrl(component.url) ? (
            <PdfViewer url={"http://localhost:8000/components/pdf?url=" + component.url} />
          ) : (
            <Center style={{ height: "100%" }}>
              <Text>Invalid PDF URL</Text>
            </Center>
          )}
        </div>
      </Flex>
    </div>
  );
};

export default ComponentCollector;
