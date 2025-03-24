document.addEventListener('DOMContentLoaded', () => {
    const filesMap = [];

    const uploadForm = document.getElementById('upload-container');
    const titleInput = document.getElementById('title');
    const mediaUploadBox = document.getElementById('media-upload-box');
    const mediaInput = document.getElementById('media-input');
    const moreMediaInput = document.getElementById('upload-more-media');
    const previewsDestination = document.getElementById('previews-destination');
    const visibilityCheckbox = document.getElementById('visibility-checkbox');


    function getUploadedImagesAmount() {
        return previewsDestination.childElementCount;
    }


    function addMediaToPost(mediaFile) {
        const preview = document.createElement('div');
        preview.className = 'preview';

        const deletePreviewButton = document.createElement('button');
        deletePreviewButton.type = 'button';
        deletePreviewButton.className = 'preview-delete';
        deletePreviewButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed">
                <path d="M280-120q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm400-600H280v520h400v-520ZM360-280h80v-360h-80v360Zm160 0h80v-360h-80v360ZM280-720v520-520Z"/>
            </svg><span>Delete</span>
        `;

        const previewContent = document.createElement('img');
        previewContent.className = 'preview-content';
        const objectURL = URL.createObjectURL(mediaFile);
        previewContent.src = objectURL;

        deletePreviewButton.addEventListener('click', () => {
            URL.revokeObjectURL(objectURL) // free memory
            previewsDestination.removeChild(preview);
            if (getUploadedImagesAmount() === 0) {
                document.body.classList.remove('has-uploaded');
            }

            const indexToRemove = filesMap.findIndex(
                item => item.object_url === objectURL
            );
            if (indexToRemove !== -1) {
                filesMap.splice(indexToRemove, 1);
            }
        });

        const previewDescription = document.createElement('textarea');
        previewDescription.className = 'preview-description';
        previewDescription.placeholder = 'Add a description';
        previewDescription.maxLength = 2_000;
        previewDescription.rows = 3;

        preview.append(deletePreviewButton, previewContent, previewDescription);
        previewsDestination.append(preview);
        document.body.classList.add('has-uploaded');

        filesMap.push(
            {
                'object_url': objectURL,
                'file': mediaFile,
                getDescription() {
                    return previewDescription.value;
                }
            }
        );

        return objectURL;
    }


    mediaInput.addEventListener('change', (event) => {
        for (const file of event.target.files) {
            addMediaToPost(file);
        }
    });

    const dragDropEvents = [
        'drag',
        'dragstart',
        'dragend',
        'dragover',
        'dragenter',
        'dragleave',
        'drop',
    ];
    const mediaContainer = document.getElementById('media-container');
    for (const eventName of dragDropEvents) {
        mediaContainer.addEventListener(eventName, (event) => {
            // prevent unwanted behaviors
            event.preventDefault();
            event.stopPropagation();
        });
    }

    for (const eventName of ['dragover', 'dragenter']) {
        mediaContainer.addEventListener(eventName, () => {
            mediaUploadBox.classList.add('dragging-over');
        });
    }

    for (const eventName of ['dragleave', 'dragend', 'drop']) {
        mediaContainer.addEventListener(eventName, () => {
            mediaUploadBox.classList.remove('dragging-over');
        });
    }

    mediaContainer.addEventListener('drop', (event) => {
        for (const file of event.dataTransfer.files) {
            addMediaToPost(file);
        }
    });

    const flowsDestination = document.getElementById('flows');
    function createFlow(flowName) {
        const flow = document.createElement('li');
        flow.className = 'flow';
        flow.innerHTML = `
            <span class="flow-name"></span>
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#ffffff"><path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/></svg>
        `;
        const nameElement = flow.querySelector('.flow-name');
        nameElement.textContent = flowName;

        return flow;
    }

    function trimCharacter(string, character) {
        let start = 0;
        let end = string.length;

        while(start < end && string[start] === character)
            ++start;

        while(end > start && string[end-1] === character)
            --end;

        return (
            (start > 0 || end < string.length)
                ? string.substring(start, end)
                : string
        );
    }


    const flowsInput = document.getElementById('flows-input');
    flowsInput.addEventListener('input', (event) => {
        flowsInput.value = flowsInput.value
            .trimStart() // user is still typing, it may be a space before a word
            .replaceAll(' ', '-') // preparing it for the next step
            .replace(/-+/g, '-') // collapse hyphens into a single hyphen
            .toLowerCase();
    });

    flowsInput.addEventListener('change', (event) => {
        // user isn't typing anymore, so we can trim hyphens from the end now
        flowsInput.value = trimCharacter(flowsInput.value, '-')
    });

    function alreadyAddedFlow(flowName) {
        for (const flow of flowsDestination.children) {
            const name = flow.firstElementChild.textContent;
            if (name === flowName) {
                return true;
            }
        }

        return false;
    }

    let flowCount = 0;
    const MAX_FLOWS = 3;

    flowsInput.addEventListener('keydown', (event) => {
        if (event.key === "Enter") {
            // avoid submitting the whole form
            event.stopPropagation();
            event.preventDefault();

            flowsInput.value = trimCharacter(flowsInput.value, '-')

            const value = flowsInput.value;
            if (!value) {
                return;
            }

            flowsInput.setCustomValidity('');
            if (!flowsInput.validity.valid) {
                flowsInput.reportValidity();
                return;
            }

            if (alreadyAddedFlow(value)) {
                flowsInput.setCustomValidity("You've already added this flow.");
                flowsInput.reportValidity();
                return;
            }

            const flow = createFlow(value);
            flowsDestination.append(flow);
            ++flowCount;

            if (flowCount >= MAX_FLOWS) {
                flowsInput.disabled = true;
            }

            flow.addEventListener('click', () => {
                flow.remove();
                --flowCount;
                flowsInput.disabled = false;
            });

            flowsInput.value = '';
        }
    });

    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (getUploadedImagesAmount() === 0) {
            // TODO: proper notification
            alert('Please upload at least 1 image/video.');
            return;
        }

        const title = titleInput.value.trim();
        const isPublic = visibilityCheckbox.checked;
        const files = [];
        for (const mapping of filesMap) {
            files.push({
                'media_file': mapping.file,
                'description': mapping.getDescription().trim()
            });
        }

        const flows = [];
        for (const flow of flowsDestination.children) {
            flows.push(flow.firstElementChild.textContent);
        }

        const result = await Api.createPost(title, files, isPublic, flows);
        const newPost = await result.json();
        // TODO: notification 'post created successfully'
        document.location.href = `/posts/${newPost.post_id}`;
    });


});
