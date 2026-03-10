// Modal functions
function showModal(text) {
    const modal = document.getElementById('modal');
    const content = document.getElementById('modalText');
    content.innerText = text;
    modal.style.display = 'flex';
}

function hideModal() {
    const modal = document.getElementById('modal');
    modal.style.display = 'none';
}

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const getServerURL = 'https://smieciarkokosiarka.neocities.org/temphostServer.txt';
let uploadedFileID = null;
let uploadedFileToken = null;
let serverURL = '';

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        updateDropZoneText(files[0].name);
    }
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        updateDropZoneText(fileInput.files[0].name);
    }
});

function updateDropZoneText(filename) {
    dropZone.querySelector('p').textContent = `Selected: ${filename}`;
    dropZone.style.borderColor = '#238636';
    dropZone.style.background = 'rgba(35, 134, 54, 0.1)';
}

const qrCode = new QRCodeStyling({
    width: 300,
    height: 300,
    type: "canvas",
    data: "",
    image: "https://i.ibb.co/7dpWFD29/fwterdsdfgsdfcg.png",
    dotsOptions: {
        color: "#4267b2",
        type: "rounded",
        gradient: {
            type: "linear",
            rotation: 0,
            colorStops: [
                { offset: 0, color: "#3498db" },
                { offset: 1, color: "#2ecc71" }
            ]
        }
    },
    backgroundOptions: {
        color: "#ffffff",
    },
    imageOptions: {
        crossOrigin: "anonymous",
        margin: 5
    }
});

let qrImageUrl = null;
async function generateQRCode(qrText) {
    const container = document.getElementById('qrCodeContainer');
    container.innerHTML = '';
    qrCode.update({
        data: qrText
    });
    qrCode.getRawData("png").then((blob) => {
        if (qrImageUrl) {
            URL.revokeObjectURL(qrImageUrl);
        }
        qrImageUrl = URL.createObjectURL(blob);
        const img = document.createElement("img");
        img.src = qrImageUrl;
        img.alt = "QR Code";
        img.style.width = "100%";
        img.style.height = "100%";
        img.style.objectFit = "contain";
        container.appendChild(img);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    fetch(getServerURL)
        .then(response => response.text())
        .then(text => { serverURL = text.trim(); })
        .catch(() => { serverURL = ''; })
        .finally(() => {
            if (!serverURL) {
                serverURL = window.location.origin;
            }
        });
    document.getElementById('tosLink').addEventListener('click', function (e) {
        e.preventDefault();
        showModal(`1. Acceptance of Terms
By accessing or using TempHost (the "Service"), a project of the NanoCloud Initiative, you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, do not use the Service.

2. Description of Service
TempHost provides temporary file hosting for a maximum of 24 hours from the time of upload. After 24 hours, all files are automatically and permanently deleted from our servers. The Service is provided "as is" and is intended for short-term, non-critical file sharing.

3. User Responsibilities

Lawful Use: You agree to use the Service only for lawful purposes and in compliance with all applicable laws. You may not use the Service to store, share, or distribute illegal, harmful, or infringing content.
Prohibited Content: You may not upload or share files that contain:

NSFW (Not Safe For Work) material, pornography, or sexually explicit content
Gore, violence, or graphic content
Other people's personal data or confidential information
Content related to illegal drugs, weapons, or other restricted substances
Viruses, malware, or any content that violates intellectual property rights or privacy rights

No Backup: The Service is not a backup solution. You are solely responsible for retaining copies of your files.

4. Data Retention and Deletion

Files are stored for 24 hours from the time of upload. After this period, files are automatically deleted and cannot be recovered.
No Guarantees: We do not guarantee the availability, security, or integrity of your files during the 24-hour period. Use the Service at your own risk.
No Liability for Data Loss: TempHost is not responsible for the loss of any data, including important files, after the 24-hour period or due to any other reason. You acknowledge and accept that all files are deleted permanently after 24 hours.

5. Privacy and Security

No Collection of Personal Data: We do not collect or store personal information unless voluntarily provided (e.g., email addresses for notifications). Any such data is deleted along with your files after 24 hours.
Third-Party Access: Files may be accessible to anyone with the direct link. You are responsible for sharing links securely.

6. Intellectual Property

You retain all rights to your uploaded files.
By uploading files, you grant TempHost a limited, non-exclusive, worldwide license to store and display your files solely for the purpose of providing the Service.

7. Disclaimer of Warranties
The Service is provided "as is" and "as available." NanoCloud Initiative makes no warranties, express or implied, regarding the Service, including but not limited to merchantability, fitness for a particular purpose, or non-infringement.

8. Limitation of Liability
To the fullest extent permitted by law, NanoCloud Initiative shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising out of or related to your use of the Service. This includes, but is not limited to, the loss of important data after the 24-hour period.

9. Termination
We reserve the right to suspend or terminate your access to the Service at any time, without notice, for any reason, including but not limited to violation of these Terms.

10. Banned Users and IP Tracking

IP Tracking: To enforce these Terms and prevent abuse, TempHost may store encrypted and hashed versions of user IP addresses. This information is used solely to identify and ban users who violate these Terms, such as by uploading prohibited content.
Banned Users: If you are found to be in violation of these Terms, your IP address may be banned from accessing the Service. Bans are permanent and at the sole discretion of NanoCloud Initiative.
No Personal Data: IP addresses are never stored in plaintext or linked to personal information. They are used exclusively for security and enforcement purposes.

11. Changes to Terms
We may update these Terms from time to time. Continued use of the Service after changes constitutes acceptance of the new Terms. We encourage you to review this page periodically.

12. Governing Law
These Terms are governed by the laws of Poland, without regard to its conflict of law principles. Any disputes shall be resolved in the courts of Warsaw, Poland.

13. Contact Information
For questions or concerns about these Terms, please contact us at krzysiek.sdw4@gmail.com.`);
    });

    document.getElementById('privacyLink').addEventListener('click', function (e) {
        e.preventDefault();
        showModal(`1. Introduction
TempHost, a project of the NanoCloud Initiative, is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard information when you use our temporary file hosting service.

2. Information We Collect

File Data: We temporarily store files you upload for up to 24 hours. After this period, all files are automatically and permanently deleted.
IP Addresses: We collect and store encrypted and hashed IP addresses solely for the purpose of identifying and banning users who violate our Terms of Service (e.g., by uploading prohibited content). IP addresses are never stored in plaintext or linked to personal information.
Voluntary Information: If you choose to provide additional information (e.g., email for notifications), we will only use it for the stated purpose and delete it along with your files after 24 hours.

3. How We Use Your Information

File Hosting: Files are stored temporarily to provide the Service and are deleted after 24 hours.
Security and Enforcement: Encrypted and hashed IP addresses are used to enforce our Terms of Service, including banning users who upload prohibited content.
No Personal Data: We do not collect, store, or process personal data beyond what is necessary to provide the Service and enforce our policies.

4. Data Retention

Files: All uploaded files are deleted after 24 hours.
IP Addresses: Encrypted and hashed IP addresses are retained only as long as necessary to enforce bans and prevent abuse.
Voluntary Information: Any additional information you provide (e.g., email) is deleted after 24 hours.

5. Data Security

We implement reasonable security measures to protect your data, including encryption and hashing of IP addresses.
However, no method of transmission over the internet or electronic storage is 100% secure. You use the Service at your own risk.

6. Third-Party Access

Files may be accessible to anyone with the direct link. You are responsible for sharing links securely.
We do not sell, trade, or otherwise transfer your information to third parties.

7. Children's Privacy

The Service is not intended for children under the age of 13. We do not knowingly collect or store personal information from children.

8. Your Rights

You have the right to access, correct, or delete your data. However, due to the temporary nature of the Service, most data is automatically deleted after 24 hours.
If you believe your IP address has been incorrectly banned, you may contact us at [your contact email] to request a review.

9. Changes to This Privacy Policy

We may update this Privacy Policy from time to time. Continued use of the Service after changes constitutes acceptance of the new policy.
We encourage you to review this page periodically for updates.

10. Contact Us
For questions or concerns about this Privacy Policy, please contact us at krzysiek.sdw4@gmail.com.`);
    });
    document.getElementById('modal').addEventListener('click', function (e) {
        if (e.target === this) {
            hideModal();
        }
    });
    document.getElementById('modalClose').addEventListener('click', hideModal);
});

document.getElementById('submitBtn').addEventListener('click', function (e) {
    e.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        document.getElementById('response').innerText = 'Please select a file first.';
        return;
    }

    const maxSize = 150 * 1024 * 1024;
    if (file.size > maxSize) {
        document.getElementById('response').innerText = 'File size exceeds 150MB.';
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('uploadProgress');
    const progressText = document.getElementById('progressText');

    progressContainer.style.display = 'block';
    progressBar.value = 0;
    progressText.textContent = '0%';
    document.getElementById('response').innerText = '';

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload');

    xhr.upload.addEventListener('progress', (event) => {
        if (!event.lengthComputable) return;
        const percent = Math.round((event.loaded / event.total) * 100);
        progressBar.value = percent;
        progressText.textContent = `${percent}%`;
    });

    xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
            document.getElementById('response').innerText = xhr.responseText;
            const match = xhr.responseText.match(/File ID:\s*(\S+)\s*\|\s*File Token \(PASSWORD FOR FILE\):\s*(\S+)/);
            if (match) {
                uploadedFileID = match[1];
                uploadedFileToken = match[2];
            } else {
                uploadedFileID = null;
                uploadedFileToken = null;
            }
        } else {
            document.getElementById('response').innerText = `Upload failed (${xhr.status})`;
        }
        console.log('Upload response:', xhr.responseText);
        console.log('Extracted ID:', uploadedFileID);
        console.log('Extracted Token:', uploadedFileToken);

        if (serverURL && uploadedFileID && uploadedFileToken) {
            const qrText = `${serverURL}/download?id=${uploadedFileID}&token=${uploadedFileToken}`;
            generateQRCode(qrText);
        }

        progressBar.value = 100;
        progressText.textContent = '100%';
        setTimeout(() => {
            progressContainer.style.display = 'none';
        }, 1500);
    });

    xhr.addEventListener('error', () => {
        document.getElementById('response').innerText = 'Upload error occurred.';
        progressContainer.style.display = 'none';
    });

    xhr.send(formData);
});

document.getElementById('downloadBtn').addEventListener('click', function () {
    const id = document.getElementById('downloadId').value;
    const token = document.getElementById('downloadToken').value;

    if (!id || !token) {
        document.getElementById('downloadResponse').innerText = 'Please provide both ID and token.';
        return;
    }

    const url = `/download?id=${encodeURIComponent(id)}&token=${encodeURIComponent(token)}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(blob => {
            const a = document.createElement('a');
            const objectUrl = URL.createObjectURL(blob);
            a.href = objectUrl;
            a.download = '';
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(objectUrl);
            document.getElementById('downloadResponse').innerText = 'Download started.';
        })
        .catch(error => {
            document.getElementById('downloadResponse').innerText = 'Error: ' + error;
        });
});
