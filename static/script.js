function copyHash() {
    const hashedValueElement = document.getElementById('hashedValue');
    if (hashedValueElement) {
        const textToCopy = hashedValueElement.innerText || hashedValueElement.textContent;
        
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(textToCopy).then(() => {
                alert('Hash copied to clipboard!');
            }).catch(err => {
                console.error('Error copying with modern API: ', err);
                fallbackCopyTextToClipboard(textToCopy);
            });
        } else {
            fallbackCopyTextToClipboard(textToCopy);
        }
    }
}

function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        const successful = document.execCommand('copy');
        if (successful) {
            alert('Hash copied to clipboard! (fallback method)');
        } else {
            alert('Sorry, copying is not supported by this browser. Please copy manually.');
            console.error('Fallback: Unable to copy');
        }
    } catch (err) {
        alert('Sorry, copying is not supported by this browser. Please copy manually.');
        console.error('Fallback: Oops, unable to copy', err);
    }

    document.body.removeChild(textArea);
}