import React from 'react';
import {
  HelpCircle,
  Bot,
  Search,
  ShieldCheck,
  Workflow
} from 'lucide-react';

const Help = () => {
  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 font-serif">
      {/* Header */}
      <div className="pb-6 border-b border-gray-200 dark:border-hclsurface-darkborder">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
          <HelpCircle className="w-6 h-6 text-brand-500" />
          <span>HCLTech Multimodal RAG Assistant &amp; Architecture Guide</span>
        </h1>
        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
          Comprehensive project guide designed for evaluators, reviewers, and enterprise demonstrations.
        </p>
      </div>

      {/* Guide Sections */}
      <div className="space-y-6 text-xs leading-relaxed text-gray-800 dark:text-gray-200">
        {/* Section 1: Concept */}
        <div className="bg-white dark:bg-hclsurface-darkcard p-6 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-2">
          <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Bot className="w-5 h-5 text-brand-500" />
            <span>1. What is Multimodal Retrieval-Augmented Generation (RAG)?</span>
          </h2>
          <p className="text-sm">
            Standard RAG systems operate purely on plain text, ignoring rich diagrams, flowcharts, schematics, and structured tables.
            Our <strong>HCLTech Multimodal RAG Assistant</strong> ingests multi-page documents, extracting and semantically indexing:
          </p>
          <ul className="list-disc list-inside space-y-1 pl-2 text-sm text-gray-700 dark:text-gray-300">
            <li><strong>Page text and headings:</strong> Extracted using PyMuPDF with page-aware semantic chunking.</li>
            <li><strong>Embedded raster images &amp; visual figures:</strong> Extracted and captioned via computer vision models and domain-grounded analyzers.</li>
            <li><strong>Embedded and standalone tables:</strong> Parsed into Markdown matrices and converted to natural-language row-column assertions for searchable vector indexing.</li>
          </ul>
        </div>

        {/* Section 2: 8-Agent Architecture */}
        <div className="bg-white dark:bg-hclsurface-darkcard p-6 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-3">
          <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Workflow className="w-5 h-5 text-brand-500" />
            <span>2. The 8 Specialized Sequential Agents</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1 text-xs">
            <div className="p-3.5 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder space-y-1">
              <span className="font-bold text-gray-900 dark:text-white text-sm block">1. Document Processing Agent</span>
              <p className="text-gray-600 dark:text-gray-400">Receives PDF/DOCX/CSV, parses structural layout, and coordinates visual/tabular extraction.</p>
            </div>
            <div className="p-3.5 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder space-y-1">
              <span className="font-bold text-gray-900 dark:text-white text-sm block">2. Image Understanding Agent</span>
              <p className="text-gray-600 dark:text-gray-400">Analyzes diagrams, charts, and circuits to generate semantic captions for multimodal vector indexing.</p>
            </div>
            <div className="p-3.5 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder space-y-1">
              <span className="font-bold text-gray-900 dark:text-white text-sm block">3. Table Understanding Agent</span>
              <p className="text-gray-600 dark:text-gray-400">Transforms multi-column matrices into structured Markdown and natural-language assertions.</p>
            </div>
            <div className="p-3.5 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder space-y-1">
              <span className="font-bold text-gray-900 dark:text-white text-sm block">4. Query Understanding Agent</span>
              <p className="text-gray-600 dark:text-gray-400">Classifies intent (numerical lookup, diagnostic, schematic) and target modality (text, table, image).</p>
            </div>
            <div className="p-3.5 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder space-y-1">
              <span className="font-bold text-gray-900 dark:text-white text-sm block">5. Retrieval Agent</span>
              <p className="text-gray-600 dark:text-gray-400">Executes hybrid dense vector similarity (70%) and BM25 keyword matching (30%) with domain filtering.</p>
            </div>
            <div className="p-3.5 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder space-y-1">
              <span className="font-bold text-gray-900 dark:text-white text-sm block">6. Evidence Validation Agent</span>
              <p className="text-gray-600 dark:text-gray-400">Inspects candidate chunks, checks for contradictions across sources, and computes corroboration scores.</p>
            </div>
            <div className="p-3.5 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder space-y-1">
              <span className="font-bold text-gray-900 dark:text-white text-sm block">7. RAG Answer Agent</span>
              <p className="text-gray-600 dark:text-gray-400">Synthesizes strictly grounded answers with inline clickable page citations [Doc:Page].</p>
            </div>
            <div className="p-3.5 bg-gray-50 dark:bg-hclsurface-dark rounded-xl border border-gray-200 dark:border-hclsurface-darkborder space-y-1">
              <span className="font-bold text-gray-900 dark:text-white text-sm block">8. Response Verification Agent</span>
              <p className="text-gray-600 dark:text-gray-400">Performs hallucination auditing against source chunks to verify factual grounding.</p>
            </div>
          </div>
        </div>

        {/* Section 3: Hybrid Retrieval */}
        <div className="bg-white dark:bg-hclsurface-darkcard p-6 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-2">
          <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Search className="w-5 h-5 text-brand-500" />
            <span>3. How Hybrid Dense-Sparse Retrieval Works</span>
          </h2>
          <p className="text-sm">
            Pure semantic vector search often misses exact model numbers, code symbols, or specific temperature limits.
            Our system calculates a weighted hybrid score:
          </p>
          <div className="p-3 bg-brand-50 dark:bg-hclsurface-dark text-center text-sm rounded-xl border border-brand-200 dark:border-hclsurface-darkborder my-2 text-brand-900 dark:text-brand-200 font-bold">
            Hybrid Score = (0.7 &times; Dense Cosine Similarity) + (0.3 &times; BM25 Keyword Overlap) &times; Modality Boost
          </div>
        </div>

        {/* Section 4: Evaluator Demonstration Flow */}
        <div className="bg-white dark:bg-hclsurface-darkcard p-6 rounded-2xl border border-gray-200 dark:border-hclsurface-darkborder shadow-sm space-y-3">
          <h2 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-brand-500" />
            <span>4. Step-by-Step Demonstration Flow</span>
          </h2>
          <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700 dark:text-gray-300">
            <li><strong>Register / Login:</strong> Create an account or sign in with your email and password.</li>
            <li><strong>Upload Document:</strong> Go to <code>Upload &amp; Ingest Document</code> and upload a technical manual PDF to trigger sequential agent extraction.</li>
            <li><strong>Inspect Pages:</strong> Go to <code>My Documents</code> to view the high-resolution page thumbnails, extracted text, and detected diagrams/tables.</li>
            <li><strong>Ask Questions &amp; Attach Files:</strong> Go to <code>Multimodal Assistant</code> to ask questions or attach an image diagram for grounded analysis.</li>
            <li><strong>Review Agent Activity:</strong> Open <code>Sequential Agent Pipeline</code> to inspect the real-time execution trace and latency of all 8 agents.</li>
            <li><strong>Run Benchmark:</strong> Go to <code>Evaluation Benchmark</code> to execute the multi-domain benchmark test suite.</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default Help;
