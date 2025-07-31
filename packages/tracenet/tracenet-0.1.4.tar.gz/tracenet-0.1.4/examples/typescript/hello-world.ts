import 'dotenv/config';
import { Agent, run } from '@openai/agents';
import '@stackgen-ai/tracenet';
import { createManualSpan, traceMethod } from '@stackgen-ai/tracenet';
//Will  autointrument tracing for all common agent frameworks

// Function with decorator for automatic tracing
class StoryProcessor {
  @traceMethod('story_enhancement', { component: 'story_processor' })
  async enhanceStory(originalStory: string): Promise<string> {
    // Simulate story enhancement processing
    await new Promise(resolve => setTimeout(resolve, 100)); // Simulate work
    
    const enhancement = "\n\n--- Story Analysis ---\n" +
      `Characters: ${this.countCharacters(originalStory)}\n` +
      `Sentences: ${this.countSentences(originalStory)}\n` +
      `Emotional tone: ${this.analyzeEmotionalTone(originalStory)}`;
    
    return originalStory + enhancement;
  }

  private countCharacters(story: string): number {
    return story.replace(/[^a-zA-Z]/g, '').length;
  }

  private countSentences(story: string): number {
    return story.split(/[.!?]+/).filter(s => s.trim().length > 0).length;
  }

  private analyzeEmotionalTone(story: string): string {
    const positiveWords = ['beautiful', 'wonderful', 'joy', 'love', 'hope', 'alive', 'light'];
    const found = positiveWords.filter(word => story.toLowerCase().includes(word));
    return found.length > 0 ? 'Positive and uplifting' : 'Neutral';
  }
}

// Function with manual subspans
async function processStoryWithSubspans(story: string): Promise<string> {
  const mainSpan = createManualSpan('story_processing_pipeline', {
    operation: 'multi_step_processing',
    input_length: story.length
  });

  return await mainSpan.wrap(async () => {
    // Subspan 1: Text analysis
    const analysisSpan = createManualSpan('text_analysis', {
      step: 1,
      analysis_type: 'linguistic'
    });
    
    const analysisResult = await analysisSpan.wrap(async () => {
      await new Promise(resolve => setTimeout(resolve, 50)); // Simulate analysis
      return {
        wordCount: story.split(' ').length,
        readingTime: Math.ceil(story.split(' ').length / 200), // words per minute
        complexity: story.split(' ').filter(word => word.length > 6).length
      };
    });

    // Subspan 2: Sentiment evaluation
    const sentimentSpan = createManualSpan('sentiment_evaluation', {
      step: 2,
      evaluation_type: 'emotional_analysis'
    });
    
    const sentimentResult = await sentimentSpan.wrap(async () => {
      await new Promise(resolve => setTimeout(resolve, 30)); // Simulate sentiment analysis
      const emotionalWords = story.toLowerCase().match(/\b(happy|sad|excited|wonder|beautiful|magical|lonely|hopeful)\b/g) || [];
      return {
        emotionalWords: emotionalWords.length,
        dominantEmotion: emotionalWords.length > 0 ? emotionalWords[0] : 'neutral',
        sentimentScore: Math.random() * 0.4 + 0.6 // Simulate positive sentiment
      };
    });

    // Subspan 3: Generate summary
    const summarySpan = createManualSpan('story_summarization', {
      step: 3,
      summary_type: 'content_extraction'
    });
    
    const summary = await summarySpan.wrap(async () => {
      await new Promise(resolve => setTimeout(resolve, 40)); // Simulate summarization
      const sentences = story.split('.');
      const firstSentence = sentences.length > 0 ? (sentences[0] || '') + '.' : 'No content available.';
      return {
        briefSummary: firstSentence,
        keyThemes: ['discovery', 'music', 'emotion', 'transformation'],
        mainCharacter: 'Robot (Lumo)'
      };
    });

    // Combine all results
    const processingReport = `
--- Story Processing Report ---
📊 Analysis: ${analysisResult.wordCount} words, ${analysisResult.readingTime} min read, complexity: ${analysisResult.complexity}
💭 Sentiment: ${sentimentResult.dominantEmotion} (score: ${sentimentResult.sentimentScore.toFixed(2)})
📝 Summary: ${summary.briefSummary}
🎯 Themes: ${summary.keyThemes.join(', ')}
👤 Main Character: ${summary.mainCharacter}
`;

    return story + processingReport;
  });
}

async function main() {
  console.log('🚀 Starting Creative Story Agent with Enhanced Tracing...\n');

  // Step 1: Generate the story with automatic tracing
  const agent = new Agent({
    name: 'Creative Story Agent',
    instructions: 'You are a creative storyteller who responds with vivid, imaginative short stories. Always include sensory details and emotions in your narratives.',
  });

  console.log('📖 Generating story...');
  const result = await run(agent, 'Tell me a story about a robot who discovers music for the first time.');
  
  console.log('✅ Story generated!\n');
  
  // Check if we have a valid story
  if (!result.finalOutput) {
    console.error('❌ No story generated. Exiting...');
    return;
  }
  
  console.log('📚 Original Story:');
  console.log('='.repeat(50));
  console.log(result.finalOutput);
  console.log('='.repeat(50));

  // Step 2: Enhance the story using decorated function
  console.log('\n🎨 Enhancing story with decorated function...');
  const processor = new StoryProcessor();
  const enhancedStory = await processor.enhanceStory(result.finalOutput);
  
  console.log('✅ Story enhanced!\n');

  // Step 3: Process the story with manual subspans
  console.log('⚙️ Processing story with detailed subspans...');
  const processedStory = await processStoryWithSubspans(enhancedStory);
  
  console.log('✅ Story processing complete!\n');
  console.log('📋 Final Result with All Processing:');
  console.log('='.repeat(60));
  console.log(processedStory);
  console.log('='.repeat(60));

  console.log('\n🎯 All operations traced! Check your Langfuse dashboard for detailed traces.');
}

if (require.main === module) {
  main().catch(console.error);
} 