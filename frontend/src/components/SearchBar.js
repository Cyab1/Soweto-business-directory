import React, { useState } from "react";

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState("");

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSearch} className="mb-4">
      <input
        type="text"
        placeholder="Search businesses..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="form-control"
      />
      <button type="submit" className="btn btn-primary mt-2">
        Search
      </button>
    </form>
  );
};

export default SearchBar;
