import React from 'react';
import { Box } from '@mantine/core';

const PDFViewer = ({ url }) => {


    return (
        // <Box sx={{ flexGrow: 1, height: '100%', width: '100%', display: 'flex' }}>
            <iframe
                src={url}
                style={{ flexGrow: 1, height: '100%', width: '100%', border: 'none' }}
                title="pdf"
            ></iframe>
        // </Box>
    );
};

export default PDFViewer;