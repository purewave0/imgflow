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

        filesMap.push(
            {'object_url': objectURL, 'file': mediaFile}
        );

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
        previewDescription.hidden = true;

        preview.append(deletePreviewButton, previewContent, previewDescription);
        previewsDestination.append(preview);
        document.body.classList.add('has-uploaded');

        return objectURL;
    }


    mediaInput.addEventListener('change', (event) => {
        addMediaToPost(event.target.files[0]);
    });

    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (getUploadedImagesAmount() === 0) {
            alert('Please upload at least 1 image/video.');
            return;
        }
        const title = titleInput.value.trim();
        const files = filesMap.map(mapping => mapping.file);
        const isPublic = visibilityCheckbox.checked;

        const result = await Api.createPost(title, files, isPublic);
        const newPost = await result.json();
        // TODO: notification 'post created successfully'
        document.location.href = `/posts/${newPost.post_id}`;
    });
});
