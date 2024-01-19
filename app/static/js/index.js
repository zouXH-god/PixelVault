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
    showToast("已复制到粘贴板")
  } catch (err) {
    console.error('Unable to copy', err);
  }

  // 移除临时创建的 textarea
  document.body.removeChild(textarea);
}

function setupDragAndDrop() {
    const dropArea = document.getElementById('upload-box');
    const fileInput = document.getElementById('upload-box-files');
    const fileListDisplay = document.getElementById('file-list-display');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('drag-over'), false);
    });

    dropArea.addEventListener('drop', e => {
        fileInput.files = e.dataTransfer.files;
        displayFiles(fileInput.files);
    }, false);

    dropArea.addEventListener('click', () => {
        fileInput.click();
    }, false);

    fileInput.addEventListener('change', () => {
        displayFiles(fileInput.files);
    }, false);

    function displayFiles(files) {
        fileListDisplay.innerHTML = '';
        for (const file of files) {
            const listItem = document.createElement('li');
            listItem.textContent = file.name;
            fileListDisplay.appendChild(listItem);
        }
    }
}

window.onload = setupDragAndDrop;

function show_img(url, img_data) {
    document.getElementById("img_info_box_fix").style.display = "block";
    document.getElementById("other_btn").innerHTML = "";
    var data = img_data.thumbnails
    // 将url赋值给img标签
    var img = document.getElementById('img_pic');
    img.src = url + "&width=300";
    // 赋值图片信息
    console.log($(".img_info"))
    $(".img_name").text(img_data.original_name);
    $(".img_time").text(img_data.upload_time);
    $(".img_size").text(img_data.size);
    $(".img_w_h").text(img_data.width + "px * " + img_data.height + "px");
    // 给原图按钮添加点击复制事件
    document.getElementById("copy_btn_orange").onclick = function () {
        copy_url(url)
    };
    console.log(img_data)
    // 给其他尺寸按钮添加点击复制事件
    for (const index in data) {
        var button = document.createElement('button');
        button.className = "copy_btn";
        button.textContent = data[index].size;
        button.onclick = function () {
            copy_url(data[index].url)
        };
        document.getElementById("other_btn").appendChild(button)
    }
    return false
}


function showToast(message) {
    // 创建提示框元素
    var toast = document.createElement('div');

    // 设置提示框内容和样式
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.left = '50%';
    toast.style.top = '50%';
    toast.style.transform = 'translate(-50%, -50%)';
    toast.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    toast.style.color = 'white';
    toast.style.padding = '16px';
    toast.style.borderRadius = '4px';
    toast.style.zIndex = 1000;
    toast.style.display = 'block';

    // 将提示框添加到文档中
    document.body.appendChild(toast);

    // 3秒后自动移除提示框
    setTimeout(function() {
        document.body.removeChild(toast);
    }, 1000);
}

