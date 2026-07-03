import { Camera } from "lucide-react";
import Webcam from "react-webcam";
import { MutableRefObject } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RefreshCw, Camera as CameraIcon } from "lucide-react";

interface CameraScannerProps {
  webcamRef: MutableRefObject<Webcam | null>;
  isCameraActive: boolean;
  preview: string | null;
  isScanningBarcode: boolean;
  resetScanner: () => void;
  captureLabelImage: () => void;
  onSendImage: () => void;
  isScanning: boolean;
}

export function CameraScanner({
  webcamRef,
  isCameraActive,
  preview,
  isScanningBarcode,
  resetScanner,
  captureLabelImage,
  onSendImage,
  isScanning
}: CameraScannerProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Camera className="size-5 text-blue-600" />
          Live Scanner
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="relative border-2 border-dashed border-gray-200 rounded-xl overflow-hidden bg-gray-100 flex items-center justify-center min-h-[300px]">
          {preview ? (
            <img
              src={preview}
              alt="Preview"
              className="max-h-full mx-auto object-contain"
            />
          ) : (
            isCameraActive ? (
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                videoConstraints={{ facingMode: "environment" }}
                className="absolute inset-0 w-full h-full object-cover"
              />
            ) : (
              <div className="text-gray-400 flex flex-col items-center">
                <Camera className="size-8 mb-2" />
                <span>Camera is off</span>
              </div>
            )
          )}

          {!preview && isScanningBarcode && isCameraActive && (
            <div className="absolute inset-0 pointer-events-none flex flex-col items-center justify-center">
              <div className="w-3/4 h-32 border-2 border-green-500/50 rounded-lg relative">
                <div className="absolute top-0 left-0 w-full h-0.5 bg-green-500 animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.8)]" style={{ animation: "scan-line 2s linear infinite" }} />
                <style>{`
                  @keyframes scan-line {
                    0% { top: 0; }
                    50% { top: 100%; }
                    100% { top: 0; }
                  }
                `}</style>
              </div>
              <div className="mt-4 bg-black/60 text-white text-xs px-3 py-1 rounded-full font-medium">
                Searching for barcode...
              </div>
            </div>
          )}
        </div>

        <div className="flex gap-2">
          {preview ? (
            <>
              <Button variant="outline" onClick={resetScanner} className="flex-1">
                <RefreshCw className="size-4 mr-2" />
                Retake
              </Button>
              <Button
                onClick={onSendImage}
                disabled={isScanning}
                className="flex-1 bg-blue-600 hover:bg-blue-700"
              >
                {isScanning ? "Processing OCR..." : "Run AI Analysis"}
              </Button>
            </>
          ) : (
            <Button
              onClick={captureLabelImage}
              disabled={!isCameraActive || isScanningBarcode}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              <CameraIcon className="size-4 mr-2" />
              Capture Expiry Label
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
