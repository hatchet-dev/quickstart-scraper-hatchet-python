"use client";
import React, { useState, useEffect } from 'react';

const API_URL = "http://localhost:8000";

const siteNames = {
  googleNews: 'Google News',
  techCrunch: 'TechCrunch'
};

export default function AppComponent() {
  const [site, setSite] = useState('googleNews'); 
  const [googleNewsArticles, setGoogleNewsArticles] = useState([]);
  const [techCrunchArticles, setTechCrunchArticles] = useState([]);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [status, setStatus] = useState("idle");
  const [messageId, setMessageId] = useState(null);

  const handleStartScraping = async () => {
    try {
      const response = await fetch(`${API_URL}/scrape`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const { messageId } = await response.json();
        setMessageId(messageId);
        setStatus("loading");
        openStream(messageId);
      } else {
        console.error("Failed to start scraping");
      }
    } catch (error) {
      console.error("Error starting scraping:", error);
    }
  };

  const openStream = (messageId) => {
    const sse = new EventSource(`${API_URL}/message/${messageId}`);

    sse.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "result") {
        const start = data.payload.start;
        if (start) {
          const googleNewsData = start.googleNewsArticles?.parse_articles?.articles || [];
          const techCrunchData = start.techCrunchArticles?.parse_articles?.articles || [];

          setGoogleNewsArticles(googleNewsData);
          setTechCrunchArticles(techCrunchData);
          setStatus("completed");
        } else {
          setStatus("completed with no data");
        }
        sse.close();
      } else if (data.type === "error") {
        setStatus("error: " + (data.payload.message || "Unknown error"));
        sse.close();
      } else {
        setStatus("in progress - " + messageId);
      }
    };

    sse.onerror = () => {
      console.error("Stream error");
      setStatus("error: Stream connection failed");
      sse.close();
    };
  };

  const getArticlesForSite = () => {
    return site === 'googleNews' ? googleNewsArticles : techCrunchArticles;
  };

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between mb-6">
        <div className="flex gap-4">
          {Object.keys(siteNames).map((key) => (
            <button 
              key={key}
              className={`px-4 py-2 rounded border ${site === key ? 'bg-gray-300 border-gray-400' : 'bg-gray-100 border-gray-200'}`} 
              onClick={() => setSite(key)}
            >
              {siteNames[key]}
            </button>
          ))}
        </div>
        <button 
          className="bg-blue-500 text-white px-4 py-2 rounded" 
          onClick={handleStartScraping}
        >
          Start Scraping
        </button>
      </div>

      <div className="text-center mb-6">
        {status === "loading" ? (
          <span className="text-lg font-bold text-yellow-600">
            Loading... Scraping ID: {messageId}
          </span>
        ) : (
          <span className={`text-lg font-bold ${status === "completed" ? "text-green-600" : "text-yellow-600"}`}>
            {status === "idle" ? "Click 'Start Scraping' to begin" : `Scraping Status: ${status}`}
          </span>
        )}
      </div>

      <div className="flex gap-6">
        <div className="w-1/3 border rounded p-4">
          <h2 className="text-xl font-bold mb-4">{siteNames[site]} Articles</h2>
          {getArticlesForSite().length > 0 ? (
            <ul className="space-y-2">
              {getArticlesForSite().map((article) => (
                <li 
                  key={article.link} 
                  className={`p-2 rounded cursor-pointer border ${selectedArticle?.link === article.link ? 'bg-gray-200 border-gray-300' : 'border-gray-200'}`}
                  onClick={() => setSelectedArticle(article)}
                >
                  <div className="font-medium">{article.title}</div>
                  <div className="text-sm text-gray-500 mt-1">
                    {article.author}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-gray-500">
              {status === "completed" ? "No articles found." : "Start scraping to view articles."}
            </div>
          )}
        </div>

        <div className="w-2/3 border rounded p-4">
          <h2 className="text-xl font-bold mb-4">Article Details</h2>
          {selectedArticle ? (
            <div>
              <h3 className="text-lg font-bold mb-2">{selectedArticle.title}</h3>
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="bg-gray-200 px-2 py-1 rounded">
                  Author: {selectedArticle.author}
                </span>
                <span className="bg-gray-200 px-2 py-1 rounded">
                  Published: {selectedArticle.published_time}
                </span>
              </div>
              <a href={selectedArticle.link} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">
  Read the full article
</a>            </div>
          ) : (
            <div className="text-gray-500">
              {getArticlesForSite().length > 0 ? "Select an article to view details." : "No article selected."}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
