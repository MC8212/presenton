"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2, Cpu, AlertCircle } from "lucide-react";
import { TemplateProvider } from "../hooks/useTemplateProvider";

interface TemplateProviderSelectorProps {
  providers: TemplateProvider[];
  selectedProvider: string | null;
  onProviderChange: (provider: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
  error?: string | null;
}

const PROVIDER_ICONS: Record<string, string> = {
  openai: "OpenAI",
  google: "Google Gemini",
  anthropic: "Anthropic Claude",
  custom: "Custom (OpenRouter)",
};

export default function TemplateProviderSelector({
  providers,
  selectedProvider,
  onProviderChange,
  disabled = false,
  isLoading = false,
  error = null,
}: TemplateProviderSelectorProps) {
  if (isLoading) {
    return (
      <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg">
        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        <span className="text-sm text-muted-foreground">Loading providers...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-lg">
        <AlertCircle className="h-4 w-4" />
        <span className="text-sm">{error}</span>
      </div>
    );
  }

  if (providers.length === 0) {
    return (
      <div className="flex items-center gap-2 p-3 bg-amber-500/10 text-amber-600 rounded-lg">
        <AlertCircle className="h-4 w-4" />
        <span className="text-sm">
          No LLM providers configured. Please configure at least one provider in settings.
        </span>
      </div>
    );
  }

  const selectedProviderInfo = providers.find((p) => p.id === selectedProvider);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium flex items-center gap-2">
        <Cpu className="h-4 w-4" />
        AI Provider for Template Extraction
      </label>
      <Select
        value={selectedProvider || undefined}
        onValueChange={onProviderChange}
        disabled={disabled}
      >
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Select a provider" />
        </SelectTrigger>
        <SelectContent>
          {providers.map((provider) => (
            <SelectItem key={provider.id} value={provider.id}>
              <div className="flex flex-col items-start">
                <span className="font-medium">{provider.name}</span>
                <span className="text-xs text-muted-foreground">
                  Model: {provider.model}
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {selectedProviderInfo && (
        <p className="text-xs text-muted-foreground">
          Using {selectedProviderInfo.name} ({selectedProviderInfo.model}) for
          slide-to-HTML and HTML-to-React conversions.
        </p>
      )}
    </div>
  );
}
