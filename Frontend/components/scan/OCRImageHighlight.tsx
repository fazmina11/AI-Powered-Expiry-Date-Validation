"use client";

import { useState, useRef, useEffect } from "react";

interface OCRBlock {
  text: string;
  confidence: number;
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
}

interface OCRImageHighlightProps {
  imageUrl: string;
  ocrBlocks: {
    width: number;
    height: number;
    blocks: OCRBlock[];
  } | null;
}

export function OCRImageHighlight({ imageUrl, ocrBlocks }: OCRImageHighlightProps) {
  const [hoveredBlock, setHoveredBlock] = useState<OCRBlock | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });

  // Get image original size if not provided by backend
  useEffect(() => {
    if (!imageUrl) return;
    const img = new Image();
    img.src = imageUrl;
    img.onload = () => {
      setImageSize({ width: img.naturalWidth, height: img.naturalHeight });
    };
  }, [imageUrl]);

  const originalWidth = ocrBlocks?.width || imageSize.width || 1;
  const originalHeight = ocrBlocks?.height || imageSize.height || 1;
  const blocks = ocrBlocks?.blocks || [];

  return (
    <div className="relative w-full flex flex-col items-center select-none bg-slate-950 rounded-lg border border-slate-800 overflow-hidden">
      {/* Image Container */}
      <div ref={containerRef} className="relative w-full max-w-full aspect-auto flex justify-center bg-black/40">
        <img
          src={imageUrl}
          alt="Scanned product label"
          className="w-full h-auto object-contain block max-h-[300px]"
        />

        {/* SVG Overlay */}
        <svg
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
          viewBox={`0 0 ${originalWidth} ${originalHeight}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {blocks.map((block, idx) => {
            const width = block.x_max - block.x_min;
            const height = block.y_max - block.y_min;

            return (
              <rect
                key={idx}
                x={block.x_min}
                y={block.y_min}
                width={width}
                height={height}
                fill="rgba(59, 130, 246, 0.12)"
                stroke="rgba(59, 130, 246, 0.65)"
                strokeWidth={Math.max(originalWidth / 450, 1.5)}
                className="pointer-events-auto cursor-help transition-all duration-150 hover:fill-blue-500/25 hover:stroke-blue-400"
                onMouseEnter={() => setHoveredBlock(block)}
                onMouseLeave={() => setHoveredBlock(null)}
              />
            );
          })}
        </svg>
      </div>

      {/* Tooltip or status box below */}
      <div className="w-full bg-slate-900 border-t border-slate-800 p-3 min-h-[56px] flex items-center justify-between text-xs transition-colors duration-200">
        {hoveredBlock ? (
          <>
            <div className="flex-1 pr-4">
              <span className="text-slate-500 block uppercase tracking-wider text-[10px]">Detected Text</span>
              <span className="font-mono text-slate-200 font-semibold break-all">{hoveredBlock.text}</span>
            </div>
            <div className="text-right shrink-0">
              <span className="text-slate-500 block uppercase tracking-wider text-[10px]">Confidence</span>
              <span className={`font-semibold ${(hoveredBlock.confidence >= 0.85) ? 'text-emerald-400' : 'text-amber-400'}`}>
                {(hoveredBlock.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </>
        ) : (
          <div className="text-slate-500 flex items-center gap-2">
            <span className="size-1.5 rounded-full bg-blue-500 animate-pulse" />
            Hover over highlighted boxes in the image to inspect extracted texts.
          </div>
        )}
      </div>
    </div>
  );
}
