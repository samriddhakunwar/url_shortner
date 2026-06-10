// Utility: copy text to clipboard
function copyToClipboard() {
  var el = document.getElementById('short-url-text');
  if (el) {
    navigator.clipboard.writeText(el.textContent.trim());
  }
}
