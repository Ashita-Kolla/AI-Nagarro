import { useEffect, useRef } from 'react';

export function MermaidChart({ chart }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current && chart && window.mermaid) {
      containerRef.current.innerHTML = '';
      let cleanChart = String(chart).trim();
      if (cleanChart.startsWith('```mermaid')) cleanChart = cleanChart.substring(10);
      else if (cleanChart.startsWith('```')) cleanChart = cleanChart.substring(3);
      if (cleanChart.endsWith('```')) cleanChart = cleanChart.substring(0, cleanChart.length - 3);
      cleanChart = cleanChart.trim();

      const id = `mermaid-${Math.floor(Math.random() * 10000)}`;
      window.mermaid.render(id, cleanChart).then(({ svg }) => {
        if (svg.includes("Syntax error")) {
          throw new Error("Mermaid Syntax Error");
        }
        containerRef.current.innerHTML = svg;
      }).catch(e => {
        containerRef.current.innerHTML = `<div class="text-red-400 text-xs p-3 bg-red-900/20 border border-red-800/50 rounded flex flex-col gap-2"><span><b>Mermaid Syntax Error</b></span><span class="opacity-80">The agent generated invalid diagram code. Expand "Show raw mermaid syntax" below to see it.</span></div>`;
        const errorSvg = document.getElementById('d' + id);
        if (errorSvg) errorSvg.remove();
        const errorContainer = document.getElementById(id);
        if (errorContainer) errorContainer.remove();
      });
    }
  }, [chart]);

  return <div ref={containerRef} className="w-full bg-gray-800 rounded-lg p-4 overflow-auto border border-gray-700 flex justify-center mt-2"></div>;
}
