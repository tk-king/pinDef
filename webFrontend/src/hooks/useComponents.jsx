const useComponents = () => {
    const downloadAll = async () => {
        try {
            const response = await fetch('http://localhost:8000/components/download');
            if (!response.ok) {
                throw new Error('Failed to download components');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'components.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download error:', error);
        }
    };

    return { downloadAll };
};

export default useComponents;