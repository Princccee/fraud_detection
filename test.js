async function uploadFile(event) {
    event.preventDefault();
    let fileInput = document.getElementById("fileUpload");
    let formData = new FormData();
    formData.append("file", fileInput.files[0]);

    let response = await fetch("http://your-api-url.com/file-upload", {
        method: "POST",
        body: formData
    });

    let data = await response.json();
    
    if (response.ok) {
        console.log("Analysis Results:", data.Averages);
        
        // Display Images
        let imageContainer = document.getElementById("imageContainer");
        imageContainer.innerHTML = "";  // Clear previous images

        Object.keys(data.images).forEach(imageName => {
            let img = document.createElement("img");
            img.src = "data:image/jpeg;base64," + data.images[imageName];
            img.alt = imageName;
            img.style.width = "300px";  // Resize if needed
            imageContainer.appendChild(img);
        });
    } else {
        console.error("Error:", data);
    }
}
