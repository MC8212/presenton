import { useState, useEffect, useCallback } from "react";

export interface TemplateProvider {
  id: string;
  name: string;
  model: string;
  available: boolean;
}

interface AvailableProvidersResponse {
  providers: TemplateProvider[];
  default: string;
  has_available: boolean;
}

export const useTemplateProvider = () => {
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [availableProviders, setAvailableProviders] = useState<TemplateProvider[]>([]);
  const [defaultProvider, setDefaultProvider] = useState<string>("openai");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProviders = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch("/api/v1/ppt/template-providers/available");

      if (!response.ok) {
        throw new Error("Failed to fetch available providers");
      }

      const data: AvailableProvidersResponse = await response.json();

      setAvailableProviders(data.providers);
      setDefaultProvider(data.default);

      // Set selected provider to default if not already set
      if (!selectedProvider && data.providers.length > 0) {
        setSelectedProvider(data.default);
      }
    } catch (err) {
      console.error("Error fetching template providers:", err);
      setError(err instanceof Error ? err.message : "Failed to fetch providers");
      // Fall back to empty providers list
      setAvailableProviders([]);
    } finally {
      setIsLoading(false);
    }
  }, [selectedProvider]);

  useEffect(() => {
    fetchProviders();
  }, []);

  const hasAvailableProviders = availableProviders.length > 0;

  return {
    selectedProvider,
    setSelectedProvider,
    availableProviders,
    defaultProvider,
    isLoading,
    error,
    hasAvailableProviders,
    refreshProviders: fetchProviders,
  };
};
