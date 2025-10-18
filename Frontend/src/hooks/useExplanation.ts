import { useState } from 'react';
import { useToast } from '@/hooks/use-toast';
import API_CONFIG from '@/config/api';

interface ExplanationRequest {
  section_code: string;
  section_text: string;
  context?: string;
  user_type?: string;
  explanation_style?: string;
}

interface ExplanationResponse {
  section_code: string;
  section_title: string;
  plain_language_explanation: string;
  key_points: string[];
  real_world_example?: string;
  when_applies?: string;
  punishment_explanation?: string;
  related_concepts: string[];
  confidence_score: number;
  generated_at: string;
  llm_model_used?: string;
}

export const useExplanation = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [explanations, setExplanations] = useState<Record<string, ExplanationResponse>>({});
  const { toast } = useToast();

  const generateExplanation = async (request: ExplanationRequest): Promise<ExplanationResponse | null> => {
    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/explain`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error Response:', errorText);
        throw new Error(`Failed to generate explanation: ${response.status} ${response.statusText}`);
      }

      const explanation: ExplanationResponse = await response.json();
      
      // Store explanation in state
      setExplanations(prev => ({
        ...prev,
        [request.section_code]: explanation
      }));

      toast({
        title: "Explanation Generated",
        description: "Plain-language explanation has been generated successfully.",
      });

      return explanation;
    } catch (error) {
      console.error('Error generating explanation:', error);
      toast({
        title: "Explanation Failed",
        description: "Could not generate explanation. Please try again.",
        variant: "destructive",
      });
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const getExplanation = (sectionCode: string): ExplanationResponse | null => {
    return explanations[sectionCode] || null;
  };

  const clearExplanation = (sectionCode: string) => {
    setExplanations(prev => {
      const updated = { ...prev };
      delete updated[sectionCode];
      return updated;
    });
  };

  return {
    generateExplanation,
    getExplanation,
    clearExplanation,
    isLoading,
    explanations
  };
};