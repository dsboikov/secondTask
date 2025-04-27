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

// Проверка наличия таблицы изображений и заполнение ее данными
if(tbody) {
    // Получение текущей страницы из параметров URL
    const urlParams = new URLSearchParams(window.location.search);
    const page = Math.max(1, parseInt(urlParams.get('page')) || 1);
    const limit = parseInt(urlParams.get('limit')) || 10;

    // Если страница меньше 1, перенаправляем на первую страницу
    if (page < 1) {
        window.location.href = '/images/?page=1';
    }

	// Загрузка данных о количестве изображений и обработка пагинации
    fetch('/api/images_count/')
    .then(response => response.json())
    .then(({ count }) => {
        const imagesCount = count;
        const pagesCount = Math.ceil(imagesCount / 10);

        // Если запрошенная страница больше общего числа страниц, перенаправляем на последнюю
        if (page > pagesCount && pagesCount > 0) {
            window.location.href = `/images/?page=${pagesCount}`;
        }

        // Если есть хоть одна страница с изображениями, добавляем кнопки пагинации и загружаем изображения
        if (pagesCount >= 1) {
            // Создание кнопок пагинации
            addPagination(page, pagesCount);

            // Получение изображений для текущей страницы
            fetch('/api/images/', { headers: { 'Page': page, 'Limit': limit } })
            .then(response => response.json())
            .then(({ images }) => setImages(images));
        }
    });
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
			handleFiles(fileInput.files);
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
			info('error', 'Ошибка копирования: ' + err);
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
	.then(response => response.json())
	.then(data => {
		if(data.code == 413) {
			info('error', 'Ошибка загрузки: файл слишком большой');
		}else if(data.code == 415) {
			info('error', 'Ошибка загрузки: тип файла не поддерживается');
		}else{
			document.getElementById('uploadUrl').value = data.location;
			copyButton.disabled = false;
			info('success', 'Файл загружен');
			dropArea.classList.add('success');
			setTimeout(() => {
				dropArea.classList.remove('success');
			}, 2000)
		}
	})
	.catch(error => {
		info('error', 'Ошибка загрузки:' + error);
		console.error('Ошибка загрузки:', error);
		dropArea.classList.add('error');
	});
		
}

function setImages(images) {
    const imagesContainer = document.getElementById('imagesTableBody');
    images.forEach(image => {
		const fullname = image.filename + image.file_type;
        const tr = document.createElement('tr');
        const cells = [
            { content: `<img src="/images/${fullname}" onclick="showModalImg('/images/${fullname}')" width="42" height="100%">` },
            { content: `<a href="/images/${fullname}" target="_blank">${image.filename}</a>` },
            { content: image.original_name },
            { content: `${Math.round(image.size / 1024)} KB` },
            { content: image.upload_time },
            { content: image.file_type },
            { content: createDeleteButton(fullname) }
        ];

        cells.forEach(({ content }) => {
            const td = document.createElement('td');
            td.innerHTML = content;
            tr.appendChild(td);
        });

        imagesContainer.appendChild(tr);

    });
}

function info(infoType, infoText) {
	let infoPlace = document.getElementById('info');
	infoPlace.textContent = infoText;
	infoPlace.classList.add(infoType);
	
	setTimeout(() => {
		infoPlace.textContent = '';
		infoPlace.classList.remove(infoType);
    }, 3000)
}

// Функция для открытия модального окна с изображением
function showModalImg(src) {
	modal.classList.add('opened');
	modalImage[0].innerHTML = `<img src="${src}">`;
}

// Функция для создания кнопки удаления
function createDeleteButton(fullname) {
    return `
        <button class="delete-btn" onclick="deleteImage('${fullname}')">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-x-lg" viewBox="0 0 16 16">
                <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/>
            </svg>
        </button>
    `;
}

// Функция для удаления изображения
function deleteImage(fullname) {
    fetch(`/api/delete/${fullname}`, { method: 'DELETE' })
        .then(() => location.reload());
}



// Функция для создания кнопок пагинации
function addPagination(currentPage, totalPages) {
    const paginationContainer = document.getElementById('pagination');

    // Добавление кнопки "назад"
    addPaginationButton(currentPage - 1, '⟵', false, totalPages);

    // Добавление кнопок для всех страниц
    for (let i = 1; i <= totalPages; i++) {
        addPaginationButton(i, '', i === currentPage, totalPages);
    }

    // Добавление кнопки "вперед"
    addPaginationButton(currentPage + 1, '⟶', false, totalPages);
}

// Функция для добавления одной кнопки пагинации
function addPaginationButton(page, text, active, totalPages) {
    let element;
    if (page < 1 || page > totalPages || active) {
        element = document.createElement('span');
    } else {
        element = document.createElement('a');
        element.href = `/images/?page=${page}`;
    }

    if (active) {
        element.classList.add('active');
    }

    text = text || page;
    element.textContent = text;

    document.getElementById('pagination').appendChild(element);
}