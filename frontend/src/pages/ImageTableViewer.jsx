import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Image as ImageIcon,
  Table as TableIcon,
  ExternalLink,
  Layers,
  Sparkles,
  Search,
  Filter
} from 'lucide-react';
import { getDocuments, getDocumentDetails } from '../services/apiService';

const ImageTableViewer = () => {
  const [activeTab, setActiveTab] = useState('images'); // 'images' or 'tables'
  const [allImages, setAllImages] = useState([]);
  const [allTables, setAllTables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchAllAssets = async () => {
      try {
        const docRes = await getDocuments();
        if (docRes.status === 'success') {
          const imageList = [];
          const tableList = [];

          for (const doc of docRes.documents) {
            const detailRes = await getDocumentDetails(doc.id);
            if (detailRes.status === 'success') {
              detailRes.images.forEach((img) => {
                imageList.push({
                  ...img,
                  document_name: doc.filename,
                  domain: doc.domain,
                });
              });
              detailRes.tables.forEach((tbl) => {
                tableList.push({
                  ...tbl,
                  document_name: doc.filename,
                  domain: doc.domain,
                });
              });
            }
          }

          setAllImages(imageList);
          setAllTables(tableList);
        }
      } catch (err) {
        console.error('Error loading visual assets:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAllAssets();
  }, []);

  const filteredImages = allImages.filter(
    (img) =>
      img.document_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      img.generated_description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      img.domain.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredTables = allTables.filter(
    (tbl) =>
      tbl.document_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tbl.raw_markdown.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tbl.domain.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200 dark:border-gray-700">
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2.5">
            <ImageIcon className="w-5 h-5 text-brand-600 dark:text-brand-400" />
            <span>Extracted Visual Figures & Structured Tables Gallery</span>
          </h1>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Browse and verify all multimodal elements detected and indexed across the repository.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center p-1 bg-gray-100 dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab('images')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'images'
                ? 'bg-white dark:bg-gray-900 text-brand-600 dark:text-brand-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <ImageIcon className="w-4 h-4" />
            <span>Extracted Figures ({allImages.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('tables')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'tables'
                ? 'bg-white dark:bg-gray-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <TableIcon className="w-4 h-4" />
            <span>Structured Tables ({allTables.length})</span>
          </button>
        </div>
      </div>

      {/* Search Filter */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
        <input
          type="text"
          placeholder={`Search ${activeTab === 'images' ? 'figures by caption or domain' : 'tables by content or domain'}...`}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-9 pr-3 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-brand-500 focus:border-brand-500"
        />
      </div>

      {loading ? (
        <div className="py-12 flex justify-center">
          <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : activeTab === 'images' ? (
        /* Images Gallery */
        filteredImages.length === 0 ? (
          <div className="text-center py-12 text-gray-400 text-xs">No images matched your query.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredImages.map((img) => (
              <div
                key={img.id}
                className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden flex flex-col justify-between"
              >
                <div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-900/60 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
                    <span className="text-xs font-bold text-gray-900 dark:text-white truncate max-w-[200px]" title={img.document_name}>
                      {img.document_name}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-brand-100 text-brand-700 dark:bg-brand-900 dark:text-brand-300">
                      Page {img.page_number}
                    </span>
                  </div>

                  <div className="p-4 flex justify-center bg-gray-100 dark:bg-gray-900/80 min-h-[180px] items-center">
                    <img
                      src={img.image_path}
                      alt={img.image_name}
                      className="max-h-44 w-auto rounded object-contain shadow-sm"
                    />
                  </div>

                  <div className="p-4 space-y-2 text-xs">
                    <div className="flex items-center justify-between text-[11px] text-gray-500 dark:text-gray-400">
                      <span>Type: <strong className="text-gray-700 dark:text-gray-300">{img.image_type}</strong></span>
                      <span>Domain: <strong className="text-brand-600 dark:text-brand-400">{img.domain}</strong></span>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-900/50 p-2.5 rounded-lg border border-gray-100 dark:border-gray-800 text-[11px] leading-relaxed">
                      <strong>AI Caption:</strong> {img.generated_description}
                    </p>
                  </div>
                </div>

                <div className="p-3 bg-gray-50 dark:bg-gray-900/40 border-t border-gray-100 dark:border-gray-700 text-right">
                  <Link
                    to={`/explorer?docId=${img.document_id}&page=${img.page_number}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline"
                  >
                    <span>View in Context</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )
      ) : (
        /* Tables Gallery */
        filteredTables.length === 0 ? (
          <div className="text-center py-12 text-gray-400 text-xs">No tables matched your query.</div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredTables.map((tbl) => (
              <div
                key={tbl.id}
                className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-5 space-y-3 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-gray-900 dark:text-white">
                      {tbl.document_name} &mdash; Table #{tbl.table_index}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300">
                      Page {tbl.page_number}
                    </span>
                  </div>

                  <div className="p-3 bg-gray-50 dark:bg-gray-900/80 rounded-xl border border-gray-200 dark:border-gray-700 font-mono text-[11px] text-gray-800 dark:text-gray-200 overflow-x-auto whitespace-pre leading-relaxed max-h-52">
                    {tbl.raw_markdown}
                  </div>

                  <div className="p-2.5 bg-emerald-50/60 dark:bg-emerald-950/40 rounded-lg border border-emerald-200 dark:border-emerald-800 text-[11px] text-emerald-900 dark:text-emerald-200 mt-3">
                    <strong>Natural Language Grounding:</strong>
                    <p className="mt-0.5 leading-relaxed line-clamp-3">{tbl.natural_language_text}</p>
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between text-xs">
                  <span className="text-gray-500 dark:text-gray-400">
                    Dimensions: <strong>{tbl.row_count} rows &times; {tbl.column_count} cols</strong>
                  </span>
                  <Link
                    to={`/explorer?docId=${tbl.document_id}&page=${tbl.page_number}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline"
                  >
                    <span>Inspect Page {tbl.page_number}</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  );
};

export default ImageTableViewer;
