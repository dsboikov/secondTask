const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('fileInput');
const browseButton = document.getElementById('browseButton');
const uploadUrlInput = document.getElementById('uploadUrl');
const copyButton = document.getElementById('copyButton');
const btnGoToImages = document.getElementById('btnGoToImages');
const tbody = document.getElementById('imagesTableBody');
const modal = document.getElementById('modal');
const closeBtn = document.getElementsByClassName('close');
const modalImage = document.getElementsByClassName('modal-image');
const heroImages = [
	'/img/hero/hero1.png',
	'/img/hero/hero2.png',
	'/img/hero/hero3.png',
	'/img/hero/hero4.png',
	'/img/hero/hero5.png'
];

if(tbody) {
	fetch('/api/images/').then(response => response.json()).then(images => setImages(images.images));
}

if(modal) {
	closeBtn[0].addEventListener('click', (event) => {
		modal.classList.remove('opened');
		modalImage[0].innerHTML = '';
	});
}

if(btnGoToImages) {
	btnGoToImages.addEventListener('click', (event) => {
		window.location.href = '/images/';
	});
}

document.addEventListener('DOMContentLoaded', () => {
	const randomIndex = Math.floor(Math.random() * heroImages.length);
	const randomImage = heroImages[randomIndex];
	const heroImageEl = document.getElementById('heroImage');
	if (heroImageEl) {
		heroImageEl.src = randomImage;
	}
});

if(browseButton) {
	browseButton.addEventListener('click', () => {
		fileInput.click();
	});
}

if(dropArea) {	
	dropArea.addEventListener('click', () => {
		fileInput.click();
	});
}

if(dropArea) {
	dropArea.addEventListener('dragover', (e) => {
		e.preventDefault();
		dropArea.classList.add('dragover');
	});

	dropArea.addEventListener('dragleave', () => {
		dropArea.classList.remove('dragover');
	});

	dropArea.addEventListener('drop', (e) => {
		e.preventDefault();
		dropArea.classList.remove('dragover');
		const files = e.dataTransfer.files;
		if (files.length) {
			fileInput.files = files;
			handleFiles(fileInput.files, 'dragover');
		}
	});
}

if(fileInput) {
	fileInput.addEventListener('change', () => {
		if(typeof fileInput.files !== 'undefined') {
			handleFiles(fileInput.files, 'test');
		}
	});
}

if(copyButton) {
	copyButton.addEventListener('click', () => {
		navigator.clipboard.writeText(uploadUrlInput.value)
		.then(() => {
			copyButton.textContent = 'Copied!';
			info('success', 'Скопировано в буфер');
			copyButton.style.backgroundColor = '#7B7B7B';
			setTimeout(() => {
				copyButton.style.backgroundColor = '#0066FF';
			}, 2000);
		})
		.catch((err) => {
			info('error', 'Failed to copy: ' + err);
		});
	});
}

function handleFiles(files) {
	const file = files[0];
	if (!file) return;

	if (!['image/jpeg','image/png','image/gif', 'image/jpg'].includes(file.type)) {
		info('error', 'Формат файла не поддерживается');
		dropArea.classList.add('error');
		dropArea.classList.remove('success');
		return;
	}
	
	if (file.size > 5 * 1024 * 1024) {
		info('error', 'Слишком большой файл');
		dropArea.classList.add('error');
		dropArea.classList.remove('success');
		return;
	}

	dropArea.classList.remove('error');
	uploadFile();
}

function uploadFile() {
	let file = fileInput.files[0];

	if(typeof file === 'undefined') {  
		return;
	}

	fetch('/api/upload/', {
		method: 'POST',
		headers: {
		  'Filename': file.name
		},
		body: file
	})
	.then(response => {
		
		document.getElementById('uploadUrl').value = response.headers.get('Location');
		copyButton.disabled = false;
		info('success', 'Файл загружен');
		dropArea.classList.add('success');
		setTimeout(() => {
		  dropArea.classList.remove('success');
		}, 2000)

	})
	.catch(error => {
		info('error', 'Ошибка загрузки:' + error);
		console.error('Ошибка загрузки:', error);
		dropArea.classList.add('error');
	});
		
}

function setImages(images) {
    const imagesContainer = document.createElement('div');
    images.forEach(image => {
		
		if(image == '.gitignore') {
			return;
		}
        const tr = document.createElement('tr');

        const tdPreview = document.createElement('td');
        const tdUrl = document.createElement('td');
        const tdDelete = document.createElement('td');

        const deleteButton = document.createElement('button');
        deleteButton.onclick = () => {
            fetch('/api/delete/', {
                method: 'DELETE',
                headers: {
                    'Filename': image
                }
            })
            .then(data => {
                location.reload();
            })
        }
        deleteButton.innerHTML = '<img src="/img/trash.png" width="15" height="auto">';
        tdDelete.appendChild(deleteButton);
        tdPreview.innerHTML = `<img src="/images/${image}" width="42" height="100%">`;
        deleteButton.classList.add('delete-btn');
        tdDelete.appendChild(deleteButton);
        tdPreview.innerHTML = `<img src="/images/${image}" width="42" height="100%">`;
        tdUrl.innerHTML = `<p onclick="showModalImg('/images/${image}')">${image}</p>`;

        tr.appendChild(tdPreview);
        tr.appendChild(tdUrl);
        tr.appendChild(tdDelete);

        tbody.appendChild(tr);
    });
    document.body.appendChild(imagesContainer);
}

function info(infoType, infoText) {
	const infoPlace = document.getElementById('info');
	infoPlace.textContent = infoText;
	infoPlace.classList.add(infoType);
	
	setTimeout(() => {
		infoPlace.textContent = '';
		infoPlace.classList.remove(infoType);
    }, 3000)
}

function showModalImg(src) {
	modal.classList.add('opened');
	modalImage[0].innerHTML = `<img src="${src}">`;
}