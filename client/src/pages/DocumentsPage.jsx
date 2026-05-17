import { useState, useEffect } from "react";
import { documentService } from "../services/documentService";

export default function DocumentsPage() {
    const [file, setFile] = useState(null);
    const [title, setTitle] = useState("");
    const [message, setMessage] = useState("");
    const [documents, setDocuments] = useState([]);

    const fetchDocuments = async () => {
        try {
            const response = await fetch("http://localhost:8084/documents");
            const data = await response.json();
            setDocuments(data);
        } catch (error) {
            console.error(error);
        }
    };

    useEffect(() => {
        fetchDocuments();
    }, []);

    const handleUpload = async () => {
        if (!file || !title) {
            setMessage("Please select a file and enter a title.");
            return;
        }
        const MAX_SIZE = 5 * 1024 * 1024; // 5 MB

        if (file.size > MAX_SIZE) {
            setMessage("File is too large. Maximum allowed size is 5 MB.");
            return;
        }
        try {
            const courseId = 1;

            const uploadResponse = await documentService.uploadDocument(file, title, courseId);
            console.log("Upload response:", uploadResponse);

            const fileUrl = `/uploads/${file.name}`;

            const createResponse = await fetch("http://localhost:8084/documents", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    title: title,
                    fileName: file.name,
                    fileType: file.type || "UNKNOWN",
                    fileSize: file.size,
                    fileUrl: fileUrl,
                    uploadedBy: "11111111-1111-1111-1111-111111111111",
                    workspaceId: "22222222-2222-2222-2222-222222222222",
                }),
            });

            if (!createResponse.ok) {
                throw new Error("Metadata save failed");
            }

            const createdDocument = await createResponse.json();
            console.log("Created document:", createdDocument);

            setMessage("Upload successful and document saved!");
            setTitle("");
            setFile(null);
            await fetchDocuments();
        } catch (error) {
            console.error(error);
            setMessage("Upload failed");
        }
    };

    return (
        <div style={{ padding: "40px", color: "#111827" }}>
            <div
                style={{
                    maxWidth: "700px",
                    background: "#ffffff",
                    borderRadius: "16px",
                    padding: "32px",
                    boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
                    border: "1px solid #e5e7eb",
                }}
            >
                <h2 style={{ marginTop: 0, marginBottom: "10px", color: "#111827" }}>
                    Upload Document
                </h2>

                <p style={{ marginTop: 0, marginBottom: "20px", color: "#6b7280" }}>
                    Upload a file and give it a title.
                </p>

                <input
                    type="text"
                    placeholder="Enter document title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    style={{
                        width: "100%",
                        padding: "12px 14px",
                        marginBottom: "16px",
                        border: "1px solid #d1d5db",
                        borderRadius: "10px",
                        fontSize: "14px",
                        color: "#111827",
                        background: "#ffffff",
                    }}
                />

                <label
                    htmlFor="fileUpload"
                    style={{
                        display: "inline-block",
                        marginBottom: "16px",
                        padding: "12px 18px",
                        background: "#f3f4f6",
                        color: "#111827",
                        border: "1px solid #d1d5db",
                        borderRadius: "10px",
                        cursor: "pointer",
                    }}
                >
                    Choose File
                </label>

                <input
                    id="fileUpload"
                    type="file"
                    onChange={(e) => setFile(e.target.files[0])}
                    style={{ display: "none" }}
                />

                <div style={{ marginBottom: "16px", color: "#374151" }}>
                    {file ? file.name : "No file selected"}
                </div>

                <button
                    onClick={handleUpload}
                    style={{
                        background: "#4f46e5",
                        color: "#ffffff",
                        border: "none",
                        borderRadius: "10px",
                        padding: "12px 18px",
                        fontSize: "14px",
                        cursor: "pointer",
                    }}
                >
                    Upload
                </button>

                {message && (
                    <div
                        style={{
                            marginTop: "16px",
                            padding: "12px 14px",
                            borderRadius: "10px",
                            background: "#f3f4f6",
                            color: "#111827",
                            border: "1px solid #e5e7eb",
                        }}
                    >
                        {message}
                    </div>
                )}

                <div style={{ marginTop: "30px" }}>
                    <h3>Uploaded Documents</h3>

                    {documents.length === 0 && <p>No documents yet</p>}

                    {documents.map((doc) => (
                        <div
                            key={doc.id}
                            style={{
                                padding: "12px",
                                marginTop: "10px",
                                border: "1px solid #e5e7eb",
                                borderRadius: "10px",
                            }}
                        >
                            <div><strong>{doc.title}</strong></div>
                            <div style={{ fontSize: "13px", color: "#6b7280" }}>
                                {doc.fileName}
                            </div>
                            <div style={{ fontSize: "12px", color: "#9ca3af" }}>
                                Size: {(doc.fileSize / 1024).toFixed(1)} KB
                            </div>
                            <div style={{ fontSize: "12px", color: "#9ca3af" }}>
                                Uploaded: {doc.createdAt ? new Date(doc.createdAt).toLocaleString() : "N/A"}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}