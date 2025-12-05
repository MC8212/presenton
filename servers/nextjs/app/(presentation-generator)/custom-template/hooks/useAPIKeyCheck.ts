import { useState, useEffect } from "react";

export const useAPIKeyCheck = () => {
  const [hasRequiredKey, setHasRequiredKey] = useState(false);
  const [isRequiredKeyLoading, setIsRequiredKeyLoading] = useState(true);

  useEffect(() => {
    // Check if any vision-capable LLM provider is configured
    fetch("/api/v1/ppt/template-providers/available")
      .then((res) => res.json())
      .then((data) => {
        // has_available indicates at least one provider with a valid API key
        setHasRequiredKey(Boolean(data.has_available));
        setIsRequiredKeyLoading(false);
      })
      .catch(() => {
        // Fallback to legacy endpoint if new one fails
        fetch("/api/has-required-key")
          .then((res) => res.json())
          .then((data) => {
            setHasRequiredKey(Boolean(data.hasKey));
            setIsRequiredKeyLoading(false);
          })
          .catch(() => setIsRequiredKeyLoading(false));
      });
  }, []);

  return { hasRequiredKey, isRequiredKeyLoading };
}; 