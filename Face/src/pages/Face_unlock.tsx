import { useEffect, useRef, useState } from "react";

interface FaceUnlockProps {
    onClose: () => void;
}

function FaceUnlock({ onClose }: FaceUnlockProps) {
    const videoRef = useRef<HTMLVideoElement | null>(null);
    const streamRef = useRef<MediaStream | null>(null);

    const [cameraError, setCameraError] = useState("");

    const captureFrame = async () => {
    if (!videoRef.current) return;

    const video = videoRef.current;

    const canvas = document.createElement("canvas");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");

    if (!ctx) return;

    ctx.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );

    const blob = await new Promise<Blob | null>(
        resolve => canvas.toBlob(resolve, "image/jpeg")
    );

    if (!blob) return;

    await sendFrame(blob);
};

    const sendFrame = async (blob: Blob) => {
    const formData = new FormData();

    formData.append(
        "image",
        blob,
        "frame.jpg"
    );

    const response = await fetch(
        "http://127.0.0.1:8000/face/authenticate",
        {
            method: "POST",
            body: formData,
        }
    );

    const result = await response.json();

    console.log(result);
};

    useEffect(() => {
        let isMounted = true;

        const startCamera = async () => {
            try {
                const stream =
                    await navigator.mediaDevices.getUserMedia({
                        video: {
                            facingMode: "user",
                        },
                        audio: false,
                    });   

                // Component was closed while camera permission was loading
                if (!isMounted) {
                    stream.getTracks().forEach((track) => track.stop());
                    return;
                }

                streamRef.current = stream;

                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    console.log(videoRef.current.srcObject);
                }
            } catch (error) {
                if (!isMounted) {
                    return;
                }

                console.error("Camera error:", error);

                setCameraError(
                    "Unable to access camera. Please allow camera permission."
                );
            }
        };

        startCamera();

        return () => {
            isMounted = false;

            if (streamRef.current) {
                streamRef.current.getTracks().forEach((track) => {
                    track.stop();
                });

                streamRef.current = null;
            }

            if (videoRef.current) {
                videoRef.current.srcObject = null;
            }
        };
    }, []);

    const handleClose = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach((track) => {
                track.stop();
            });

            streamRef.current = null;
        }

        if (videoRef.current) {
            videoRef.current.srcObject = null;
        }

        onClose();
    };

    return (
        <div className="fixed inset-0 flex items-center justify-center bg-black/70">
            <div className="w-full max-w-lg p-6 bg-white rounded-xl">

                <h2 className="mb-4 text-2xl font-semibold text-center">
                    Face Unlock
                </h2>

                {cameraError ? (
                    <p className="text-center text-red-500">
                        {cameraError}
                    </p>
                ) : (
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        className="w-full rounded-lg"
                    />
                )}

                <button
                    type="button"
                    onClick={handleClose}
                    className="w-full mt-4 px-4 py-2 bg-gray-500 text-white rounded-lg"
                >
                    Cancel
                </button>

            </div>
        </div>
    );
}

export default FaceUnlock;