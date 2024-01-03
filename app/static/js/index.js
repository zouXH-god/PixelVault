async function copy_url(text) {
  try {
    await copy_value(window.location.origin + text);
    console.log('Text successfully copied to clipboard');
  } catch (err) {
    console.error('Failed to copy: ', err);
  }
}

async function copy_value(text) {
  // 创建一个临时的 textarea 元素
  const textarea = document.createElement('textarea');
  textarea.value = text;

  // 设置样式以确保 textarea 不可见
  textarea.style.position = 'fixed';
  textarea.style.left = '-9999px';
  textarea.style.top = '0';

  // 将 textarea 添加到文档中
  document.body.appendChild(textarea);

  // 选中 textarea 中的文本
  textarea.focus();
  textarea.select();

  try {
    // 执行复制命令
    const successful = document.execCommand('copy');
    const msg = successful ? 'successful' : 'unsuccessful';
    console.log('Copy command was ' + msg);
  } catch (err) {
    console.error('Unable to copy', err);
  }

  // 移除临时创建的 textarea
  document.body.removeChild(textarea);
}