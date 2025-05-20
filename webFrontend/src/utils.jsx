export const isValidPDFUrl = (str) => {
    const pattern = /^(https?:\/\/)?([\w-]+\.)+[\w-]+(\/[\w-./?%&=]*)?(\?.*)?$/i;
    return pattern.test(str);
};

export const isValidPageNumber = (str) => {
    // Matching examples: 2, 4, 2-4, 1-3, 1, 2-4, 1-3, 1-3, 1-3
    const pattern = /^(?:\d+(-\d+)?(,\s*)?)+$/;
    return pattern.test(str);
}