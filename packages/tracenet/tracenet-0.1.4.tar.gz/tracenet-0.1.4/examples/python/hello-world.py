import os
import time
import asyncio
import re
from typing import Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import tracing middleware from PyPI package
from tracenet import trace, start_span, flush, set_agent_name

# For this example, we'll use OpenAI directly since there's no Python equivalent of @openai/agents yet
import openai

# Set up OpenAI client
client = openai.OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

# Function with decorator for automatic tracing
class StoryProcessor:
    @trace(name='story_enhancement')
    def enhance_story(self, original_story: str) -> str:
        """Enhance the story with analysis details."""
        # Simulate story enhancement processing
        time.sleep(0.1)  # Simulate work
        
        enhancement = "\n\n--- Story Analysis ---\n" + \
            f"Characters: {self.count_characters(original_story)}\n" + \
            f"Sentences: {self.count_sentences(original_story)}\n" + \
            f"Emotional tone: {self.analyze_emotional_tone(original_story)}"
        
        return original_story + enhancement

    def count_characters(self, story: str) -> int:
        return len(re.sub(r'[^a-zA-Z]', '', story))

    def count_sentences(self, story: str) -> int:
        sentences = re.split(r'[.!?]+', story)
        return len([s for s in sentences if s.strip()])

    def analyze_emotional_tone(self, story: str) -> str:
        positive_words = ['beautiful', 'wonderful', 'joy', 'love', 'hope', 'alive', 'light']
        found = [word for word in positive_words if word in story.lower()]
        return 'Positive and uplifting' if found else 'Neutral'


# Function with manual subspans
def process_story_with_subspans(story: str) -> str:
    """Process the story with detailed subspans for comprehensive analysis."""
    
    with start_span('story_processing_pipeline') as main_span:
        
        # Subspan 1: Text analysis
        with start_span('text_analysis') as analysis_span:
            time.sleep(0.05)  # Simulate analysis
            analysis_result = {
                'word_count': len(story.split()),
                'reading_time': max(1, len(story.split()) // 200),  # words per minute
                'complexity': len([word for word in story.split() if len(word) > 6])
            }

        # Subspan 2: Sentiment evaluation
        with start_span('sentiment_evaluation') as sentiment_span:
            time.sleep(0.03)  # Simulate sentiment analysis
            emotional_words = re.findall(
                r'\b(happy|sad|excited|wonder|beautiful|magical|lonely|hopeful)\b', 
                story.lower()
            )
            sentiment_result = {
                'emotional_words': len(emotional_words),
                'dominant_emotion': emotional_words[0] if emotional_words else 'neutral',
                'sentiment_score': 0.6 + (0.4 * len(emotional_words) / 10)  # Simulate positive sentiment
            }

        # Subspan 3: Generate summary
        with start_span('story_summarization') as summary_span:
            time.sleep(0.04)  # Simulate summarization
            sentences = story.split('.')
            first_sentence = (sentences[0] + '.') if sentences else 'No content available.'
            summary = {
                'brief_summary': first_sentence,
                'key_themes': ['discovery', 'music', 'emotion', 'transformation'],
                'main_character': 'Robot (Pex)'
            }

        # Combine all results
        processing_report = f"""
--- Story Processing Report ---
📊 Analysis: {analysis_result['word_count']} words, {analysis_result['reading_time']} min read, complexity: {analysis_result['complexity']}
💭 Sentiment: {sentiment_result['dominant_emotion']} (score: {sentiment_result['sentiment_score']:.2f})
📝 Summary: {summary['brief_summary']}
🎯 Themes: {', '.join(summary['key_themes'])}
👤 Main Character: {summary['main_character']}
"""

        return story + processing_report


def generate_story_with_openai(prompt: str) -> str:
    """Generate a story using OpenAI API with automatic tracing."""
    
    with start_span('openai_story_generation') as generation_span:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a creative storyteller who responds with vivid, imaginative short stories. Always include sensory details and emotions in your narratives."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.8
            )
            
            story = response.choices[0].message.content
            
            # Update span with generation details
            # Note: The tracenet package handles span updates automatically
            
            return story
            
        except Exception as e:
            # Error handling is automatic with tracenet
            raise


def main():
    """Main function demonstrating the enhanced tracing capabilities."""
    print('🚀 Starting Creative Story Agent with Enhanced Tracing...\n')
    
    # Can call the set_agent_name function to set the agent name for tracing if no env var is set or for overriding the env var
    # set_agent_name('CreativeStoryAgent')
    # print('🏷️ Agent name set to: CreativeStoryAgent\n')

    # Wrap the entire execution in a single trace
    with start_span('creative_story_agent_session') as session_span:
        try:
            # Step 1: Generate the story with automatic tracing
            print('📖 Generating story...')
            
            story = generate_story_with_openai(
                'Tell me a story about a robot who discovers music for the first time.'
            )
            
            print('✅ Story generated!\n')
            
            if not story:
                print('❌ No story generated. Exiting...')
                return
            
            print('📚 Original Story:')
            print('=' * 50)
            print(story)
            print('=' * 50)

            # Step 2: Enhance the story using decorated function
            print('\n🎨 Enhancing story with decorated function...')
            processor = StoryProcessor()
            enhanced_story = processor.enhance_story(story)
            
            print('✅ Story enhanced!\n')

            # Step 3: Process the story with manual subspans
            print('⚙️ Processing story with detailed subspans...')
            processed_story = process_story_with_subspans(enhanced_story)
            
            print('✅ Story processing complete!\n')
            print('📋 Final Result with All Processing:')
            print('=' * 60)
            print(processed_story)
            print('=' * 60)

            print('\n🎯 All operations traced! Check your Langfuse dashboard for detailed traces.')
            
        except Exception as e:
            print(f'❌ Error during execution: {e}')
            raise
        finally:
            # Flush traces
            flush()


if __name__ == "__main__":
    main() 